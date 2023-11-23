CREATE OR REPLACE TRIGGER race_participation_bike_owner_trigger
    BEFORE INSERT OR UPDATE ON RACEPARTICIPATION
    FOR EACH ROW
BEGIN
    IF NEW.rider_id != (SELECT RIDER_ID from BIKE where BIKE.ID = NEW.bike_id) THEN
        raise_application_error(-20001, 'Rider id ' || TO_CHAR(NEW.rider_id) || ' must match bike owner id');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_rider_trigger
    BEFORE INSERT OR UPDATE ON RIDER
    FOR EACH ROW
BEGIN
    IF 'rider' != (SELECT type from account where ID = NEW.account_id) THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(NEW.account_id) || 'must be rider');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_coordinator_trigger
    BEFORE INSERT OR UPDATE ON COORDINATOR
    FOR EACH ROW
BEGIN
    IF 'coordinator' != (SELECT type from account where ID = NEW.account_id) THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(NEW.account_id) || 'must be coordinator');
    end if;
end;

CREATE OR REPLACE TRIGGER account_type_admin_trigger
    BEFORE INSERT OR UPDATE ON ADMIN
    FOR EACH ROW
BEGIN
    IF 'admin' != (SELECT type from account where ID = NEW.account_id) THEN
        raise_application_error(-20001, 'Account type for id ' || TO_CHAR(NEW.account_id) || 'must be admin');
    end if;
end;