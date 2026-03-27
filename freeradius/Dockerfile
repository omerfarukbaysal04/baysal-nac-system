FROM freeradius/freeradius-server:latest-3.2

COPY ./mods-enabled/sql /etc/freeradius/mods-available/sql
COPY ./mods-enabled/rest /etc/freeradius/mods-available/rest

RUN ln -s /etc/freeradius/mods-available/sql /etc/freeradius/mods-enabled/sql || true
RUN ln -s /etc/freeradius/mods-available/rest /etc/freeradius/mods-enabled/rest || true

COPY ./clients.conf /etc/freeradius/clients.conf
COPY ./sites-enabled/default /etc/freeradius/sites-available/default
RUN ln -s /etc/freeradius/sites-available/default /etc/freeradius/sites-enabled/default || true