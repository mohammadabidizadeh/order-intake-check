-- Use a disposable database with docs/schema.sql installed. Safe to rerun.
BEGIN;
DO $checks$
DECLARE
    source_a bigint;
    source_b bigint;
    batch_a bigint;
    batch_b bigint;
    first_order bigint;
BEGIN
    INSERT INTO order_source(source_key) VALUES ('fixture-A') RETURNING source_id INTO source_a;
    INSERT INTO order_source(source_key) VALUES ('fixture-B') RETURNING source_id INTO source_b;
    INSERT INTO intake_batch(source_id, idempotency_key, file_sha256, catalog_sha256)
        VALUES (source_a, 'retry', repeat('a', 64), repeat('b', 64)) RETURNING batch_id INTO batch_a;
    INSERT INTO intake_batch(source_id, idempotency_key, file_sha256, catalog_sha256)
        VALUES (source_b, 'retry', repeat('a', 64), repeat('b', 64)) RETURNING batch_id INTO batch_b;
    INSERT INTO accepted_order(source_id, batch_id, external_order_id)
        VALUES (source_a, batch_a, '001') RETURNING order_pk INTO first_order;
    INSERT INTO accepted_order(source_id, batch_id, external_order_id)
        VALUES (source_b, batch_b, '001'), (source_a, batch_a, '1');
    INSERT INTO accepted_line VALUES (first_order, '01', 'ITEM-01', 1), (first_order, '1', 'ITEM-01', 999999);
    INSERT INTO intake_event(batch_id, actor_ref, event_type) VALUES (batch_a, 'reviewer', 'batch_committed');

    BEGIN
        INSERT INTO intake_batch(source_id, idempotency_key, file_sha256, catalog_sha256)
        VALUES (source_a, 'retry', repeat('c', 64), repeat('b', 64));
        RAISE EXCEPTION 'duplicate replay key accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO accepted_order(source_id, batch_id, external_order_id) VALUES (source_b, batch_a, '002');
        RAISE EXCEPTION 'cross-source batch accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO accepted_order(source_id, batch_id, external_order_id) VALUES (source_a, batch_a, '001');
        RAISE EXCEPTION 'duplicate order accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO accepted_line VALUES (first_order, '01', 'ITEM-02', 1);
        RAISE EXCEPTION 'duplicate line accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO accepted_line VALUES (first_order, '02', 'ITEM-01', 0);
        RAISE EXCEPTION 'zero quantity accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO accepted_line VALUES (first_order, '02', 'ITEM-01', 1000000);
        RAISE EXCEPTION 'over-limit quantity accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO intake_batch(source_id, idempotency_key, file_sha256, catalog_sha256)
        VALUES (source_a, 'new', repeat('0', 63), repeat('b', 64));
        RAISE EXCEPTION 'invalid file digest accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO intake_batch(source_id, idempotency_key, file_sha256, catalog_sha256)
        VALUES (source_a, 'new', repeat('0', 64), repeat('G', 64));
        RAISE EXCEPTION 'invalid catalog digest accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO intake_event(batch_id, actor_ref, event_type) VALUES (batch_a, 'reviewer', 'unknown');
        RAISE EXCEPTION 'invalid event accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END;
$checks$;
ROLLBACK;
