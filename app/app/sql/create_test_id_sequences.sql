CREATE SEQUENCE IF NOT EXISTS bike_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS classification_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS race_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS racebonus_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS raceparticipation_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS season_test_seq START WITH 10001
CREATE SEQUENCE IF NOT EXISTS account_test_seq START WITH 10001
ALTER TABLE bike MODIFY (id DEFAULT bike_test_seq.nextval)
ALTER TABLE classification MODIFY (id DEFAULT classification_test_seq.nextval)
ALTER TABLE race MODIFY (id DEFAULT race_test_seq.nextval)
ALTER TABLE racebonus MODIFY (id DEFAULT racebonus_test_seq.nextval)
ALTER TABLE raceparticipation MODIFY (id DEFAULT raceparticipation_test_seq.nextval)
ALTER TABLE season MODIFY (id DEFAULT season_test_seq.nextval)
ALTER TABLE account MODIFY (id DEFAULT account_test_seq.nextval)
COMMIT
