CREATE OR REPLACE TRIGGER race_participation_bike_owner_trigger
    BEFORE INSERT OR UPDATE ON RACEPARTICIPATION
    FOR EACH ROW
DECLARE
  r_id rider.id%type;
BEGIN
    SELECT RIDER_ID into r_id from BIKE where ID = :NEW.bike_id;
    IF :NEW.rider_id != r_id THEN
        raise_application_error(-20001, 'Rider id ' || TO_CHAR(:NEW.rider_id) || ' must match bike owner id');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_rider_trigger
    BEFORE INSERT OR UPDATE ON RIDER
    FOR EACH ROW
DECLARE
  account_type account.type%type;
BEGIN
    SELECT type into account_type from account where ID = :NEW.id;
    IF 'rider' != account_type THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(:NEW.id) || 'must be rider');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_coordinator_trigger
    BEFORE INSERT OR UPDATE ON COORDINATOR
    FOR EACH ROW
DECLARE
  account_type account.type%type;
BEGIN
    SELECT type into account_type from account where ID = :NEW.id;
    IF 'coordinator' != account_type THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(:NEW.id) || 'must be coordinator');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_admin_trigger
    BEFORE INSERT OR UPDATE ON ADMIN
    FOR EACH ROW
DECLARE
  account_type account.type%type;
BEGIN
    SELECT type into account_type from account where ID = :NEW.id;
    IF 'admin' != account_type THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(:NEW.id) || 'must be admin');
    end if;
end;