CREATE TABLE IF NOT EXISTS public."Users"
(
    chat_id bigint NOT NULL,
    datetime timestamp without time zone NOT NULL,
    platform character varying(50),
    start_date date,
    end_date date,
    brand character varying(100),
    request_category character varying(100)
)