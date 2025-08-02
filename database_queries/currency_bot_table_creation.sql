drop table if exists currency cascade;
drop table if exists currency_cost cascade;
drop table if exists user_choice cascade;

create table currency (
	currency_code varchar(3) not null unique,
	currency_num varchar(3) primary key,
	currency_name varchar(50) not null
);

create table user_choice (
	user_id bigint not null,
	currency_num varchar(3) not null references currency(currency_num),
	created_at timestamp default current_timestamp,
	primary key (user_id, currency_num)
);

create table currency_cost (
	id serial primary key,
	date timestamp not null default current_timestamp,
	currency_num varchar(3) not null references currency(currency_num),
	rate decimal(10,4) not null,
	unit integer not null,
	unique (date, currency_num)
)