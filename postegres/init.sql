-- radcheck tablosu rlm_sql sema uyumlulugu icin kalir ama sifre orada saklanmaz.
CREATE TABLE
IF NOT EXISTS users
(
    id            SERIAL PRIMARY KEY,
    username      VARCHAR
(64) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    groupname     VARCHAR
(64) NOT NULL
);

-- radcheck: FreeRADIUS rlm_sql modulu bu tabloyu bekliyor, sema uyumlulugu icin var.
CREATE TABLE
IF NOT EXISTS radcheck
(
    id          SERIAL PRIMARY KEY,
    username    VARCHAR
(64) NOT NULL,
    attribute   VARCHAR
(64) NOT NULL,
    op          CHAR
(2)     NOT NULL DEFAULT ':=',
    value       VARCHAR
(253) NOT NULL
);

-- radreply: kullaniciya donulecek attribute'ler
CREATE TABLE
IF NOT EXISTS radreply
(
    id          SERIAL PRIMARY KEY,
    username    VARCHAR
(64) NOT NULL,
    attribute   VARCHAR
(64) NOT NULL,
    op          CHAR
(2)     NOT NULL DEFAULT '=',
    value       VARCHAR
(253) NOT NULL
);

-- radusergroup: kullanici-grup iliskisi
CREATE TABLE
IF NOT EXISTS radusergroup
(
    id          SERIAL PRIMARY KEY,
    username    VARCHAR
(64) NOT NULL,
    groupname   VARCHAR
(64) NOT NULL,
    priority    INTEGER     NOT NULL DEFAULT 1
);

-- radgroupreply: grup bazli VLAN attribute'leri
CREATE TABLE
IF NOT EXISTS radgroupreply
(
    id          SERIAL PRIMARY KEY,
    groupname   VARCHAR
(64) NOT NULL,
    attribute   VARCHAR
(64) NOT NULL,
    op          CHAR
(2)     NOT NULL DEFAULT '=',
    value       VARCHAR
(253) NOT NULL
);

-- radacct: accounting kayitlari
CREATE TABLE
IF NOT EXISTS radacct
(
    radacctid           BIGSERIAL PRIMARY KEY,
    acctsessionid       VARCHAR
(64)  NOT NULL DEFAULT '',
    acctuniqueid        VARCHAR
(32)  NOT NULL DEFAULT '',
    username            VARCHAR
(64)  NOT NULL DEFAULT '',
    nasipaddress        INET         NOT NULL,
    nasportid           VARCHAR
(15)  DEFAULT NULL,
    acctstarttime       TIMESTAMPTZ  DEFAULT NULL,
    acctupdatetime      TIMESTAMPTZ  DEFAULT NULL,
    acctstoptime        TIMESTAMPTZ  DEFAULT NULL,
    acctsessiontime     BIGINT       DEFAULT NULL,
    acctinputoctets     BIGINT       DEFAULT NULL,
    acctoutputoctets    BIGINT       DEFAULT NULL,
    acctterminatecause  VARCHAR
(32)  NOT NULL DEFAULT '',
    framedipaddress     INET         DEFAULT NULL,
    callingstationid    VARCHAR
(50)  NOT NULL DEFAULT ''
);

-- nas: NAS cihaz bilgileri
CREATE TABLE
IF NOT EXISTS nas
(
    id          SERIAL PRIMARY KEY,
    nasname     VARCHAR
(128) NOT NULL,
    shortname   VARCHAR
(32)  DEFAULT NULL,
    secret      VARCHAR
(60)  NOT NULL DEFAULT 'testing123',
    description VARCHAR
(200) DEFAULT NULL
);

-- Test NAS cihazi
INSERT INTO nas
    (nasname, shortname, secret, description)
VALUES
    ('127.0.0.1', 'localhost', 'testing123', 'Test NAS');

-- Grup VLAN attribute'leri
-- Tunnel-Type 13 = VLAN, Tunnel-Medium-Type 6 = IEEE 802
INSERT INTO radgroupreply
    (groupname, attribute, op, value)
VALUES
    ('admin', 'Tunnel-Type', ':=', '13'),
    ('admin', 'Tunnel-Medium-Type', ':=', '6'),
    ('admin', 'Tunnel-Private-Group-Id', ':=', '10'),

    ('employee', 'Tunnel-Type', ':=', '13'),
    ('employee', 'Tunnel-Medium-Type', ':=', '6'),
    ('employee', 'Tunnel-Private-Group-Id', ':=', '20'),

    ('guest', 'Tunnel-Type', ':=', '13'),
    ('guest', 'Tunnel-Medium-Type', ':=', '6'),
    ('guest', 'Tunnel-Private-Group-Id', ':=', '30');

-- Test kullanicilari (bcrypt hash'li sifreler)
-- admin1 -> admin123
-- emp1   -> emp123
-- guest1 -> guest123
INSERT INTO users
    (username, password_hash, groupname)
VALUES
    ('admin1', '$2b$12$dxQo1aGWkhHoxI8jovanzeETG4TZSPU8n2R0w9s5bRbiD/7Ci94ry', 'admin'),
    ('emp1', '$2b$12$TGioWk22hSj3D4PiFHosa.ODunAkAppYSykJYgJH2GA8h7tgm5R76', 'employee'),
    ('guest1', '$2b$12$rDvJwnI4iVXqRvNYFvnAeODrQcbgci4v4U0em/4DiDBA.FU3yX1ja', 'guest');

-- radusergroup: FreeRADIUS grup sorgulari icin
INSERT INTO radusergroup
    (username, groupname, priority)
VALUES
    ('admin1', 'admin', 1),
    ('emp1', 'employee', 1),
    ('guest1', 'guest', 1);