create table if not exists currency (
	currency_code varchar(3) not null unique,
	currency_num varchar(3) primary key,
	currency_name varchar(50) not null
);

create table if not exists user_choice (
	user_id bigint not null,
	currency_num varchar(3) not null references currency(currency_num),
	created_at timestamp default current_timestamp,
	primary key (user_id, currency_num)
);

alter table user_choice
add constraint user_choice_user_id_fkey
foreign key (user_id) references users(user_id);

create table if not exists users (
	user_id bigint not null primary key,
	lang varchar(2) not null default 'ru',
);

create table if not exists currency_cost (
	id serial primary key,
	date timestamp not null default current_timestamp,
	currency_num varchar(3) not null references currency(currency_num),
	rate decimal(10,4) not null,
	unit integer not null,
	unique (date, currency_num)
);