begin;

set constraints all deferred;

update currency 
set currency_code = 'GBP' 
where currency_code = 'GBR';

commit;
