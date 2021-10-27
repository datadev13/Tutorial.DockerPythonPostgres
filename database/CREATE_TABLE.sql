create table if not exists numbers
(
    id     serial primary key,
    number int       default 0                 not null,
    ctime  timestamp default current_timestamp not null
);

create sequence numbers_seq
  start 1
  increment 1;

create unique index numbers_idx on numbers (id);