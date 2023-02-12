CREATE TABLE IF NOT EXISTS public."Users"
(
    chat_id bigint NOT NULL,
    datetime timestamp without time zone NOT NULL,
    platform character varying(50),
    segment character varying(50),
    brand character varying(100),
    subscribtion boolean,
    request_category character varying(100)
)