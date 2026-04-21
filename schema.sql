CREATE TYPE part_of_speech_enum AS ENUM (
    'n',
    'v',
    'adj',
    'adv',
    'prep',
    'pron',
    'conj',
    'interj',
    'num',
    'art'
);

CREATE TABLE word (
    id BIGSERIAL PRIMARY KEY,
    spelling VARCHAR(128) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE word_sense (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL,
    part_of_speech part_of_speech_enum NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_word_sense_word
        FOREIGN KEY (word_id) REFERENCES word(id),
    CONSTRAINT uq_word_sense_word_pos
        UNIQUE (word_id, part_of_speech)
);

CREATE TABLE meaning (
    id BIGSERIAL PRIMARY KEY,
    sense_id BIGINT NOT NULL,
    definition VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_meaning_sense
        FOREIGN KEY (sense_id) REFERENCES word_sense(id),
    CONSTRAINT uq_meaning_sense_definition
        UNIQUE (sense_id, definition)
);

CREATE TABLE review_state (
    word_id BIGINT PRIMARY KEY,
    proficiency INTEGER NOT NULL DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_review_state_word
        FOREIGN KEY (word_id) REFERENCES word(id),
    CONSTRAINT ck_review_state_proficiency_non_negative
        CHECK (proficiency >= 0)
);

CREATE TABLE study_session (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ NULL,
    reviewed_word_count INTEGER NOT NULL DEFAULT 0,
    duration_seconds INTEGER NULL
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_word_updated_at
BEFORE UPDATE ON word
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_word_sense_updated_at
BEFORE UPDATE ON word_sense
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_meaning_updated_at
BEFORE UPDATE ON meaning
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_review_state_updated_at
BEFORE UPDATE ON review_state
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
