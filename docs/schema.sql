-- Proposed single-business persistence model for phase 2. Run in a fresh PostgreSQL test database.
-- One accepted batch is committed in one transaction. Held orders stay in the operator's preview.
BEGIN;
CREATE TABLE order_source (
    source_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key text COLLATE "C" NOT NULL UNIQUE CHECK (length(source_key) BETWEEN 1 AND 64)
);

CREATE TABLE intake_batch (
    batch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id bigint NOT NULL REFERENCES order_source,
    idempotency_key text COLLATE "C" NOT NULL CHECK (length(idempotency_key) BETWEEN 1 AND 128),
    file_sha256 text COLLATE "C" NOT NULL CHECK (file_sha256 ~ '^[0-9a-f]{64}$'),
    catalog_sha256 text COLLATE "C" NOT NULL CHECK (catalog_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_id, idempotency_key),
    UNIQUE (source_id, batch_id)
);

CREATE TABLE accepted_order (
    order_pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id bigint NOT NULL,
    batch_id bigint NOT NULL,
    external_order_id text COLLATE "C" NOT NULL CHECK (length(external_order_id) BETWEEN 1 AND 64),
    FOREIGN KEY (source_id, batch_id) REFERENCES intake_batch (source_id, batch_id),
    UNIQUE (source_id, external_order_id)
);

CREATE TABLE accepted_line (
    order_pk bigint NOT NULL REFERENCES accepted_order,
    external_line_id text COLLATE "C" NOT NULL CHECK (length(external_line_id) BETWEEN 1 AND 64),
    item_code text COLLATE "C" NOT NULL CHECK (length(item_code) BETWEEN 1 AND 64),
    quantity integer NOT NULL CHECK (quantity BETWEEN 1 AND 999999),
    PRIMARY KEY (order_pk, external_line_id)
);

CREATE TABLE intake_event (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id bigint NOT NULL REFERENCES intake_batch,
    actor_ref text NOT NULL CHECK (length(actor_ref) BETWEEN 1 AND 128),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    event_type text NOT NULL CHECK (event_type IN ('batch_committed', 'batch_exported'))
);
COMMIT;
