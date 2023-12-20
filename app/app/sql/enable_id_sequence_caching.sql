ALTER SEQUENCE bike_seq CACHE 20
ALTER SEQUENCE classification_seq CACHE 20
ALTER SEQUENCE race_seq CACHE 20
ALTER SEQUENCE racebonus_seq CACHE 20
ALTER SEQUENCE raceparticipation_seq CACHE 20
ALTER SEQUENCE season_seq CACHE 20
ALTER SEQUENCE account_seq CACHE 20
ALTER TABLE bike MODIFY (id DEFAULT bike_seq.nextval)
ALTER TABLE classification MODIFY (id DEFAULT classification_seq.nextval)
ALTER TABLE race MODIFY (id DEFAULT race_seq.nextval)
ALTER TABLE racebonus MODIFY (id DEFAULT racebonus_seq.nextval)
ALTER TABLE raceparticipation MODIFY (id DEFAULT raceparticipation_seq.nextval)
ALTER TABLE season MODIFY (id DEFAULT season_seq.nextval)
ALTER TABLE account MODIFY (id DEFAULT account_seq.nextval)
commit