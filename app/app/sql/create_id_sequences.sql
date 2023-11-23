CREATE SEQUENCE IF NOT EXISTS bike_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS classification_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS classificationaccesslimiter_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS race_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS racebonus_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS raceparticipation_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS season_seq START WITH 1 CACHE 20
CREATE SEQUENCE IF NOT EXISTS account_seq START WITH 1 CACHE 20
ALTER TABLE bike MODIFY (id DEFAULT bike_seq.nextval)
ALTER TABLE classification MODIFY (id DEFAULT classification_seq.nextval)
ALTER TABLE classificationaccesslimiter MODIFY (id DEFAULT classificationaccesslimiter_seq.nextval)
ALTER TABLE race MODIFY (id DEFAULT race_seq.nextval)
ALTER TABLE racebonus MODIFY (id DEFAULT racebonus_seq.nextval)
ALTER TABLE raceparticipation MODIFY (id DEFAULT raceparticipation_seq.nextval)
ALTER TABLE season MODIFY (id DEFAULT season_seq.nextval)
ALTER TABLE account MODIFY (id DEFAULT account_seq.nextval)
COMMIT
