\d inventory_batch
                                      Table "public.inventory_batch"
        Column        |     Type      | Collation | Nullable |                   Default
----------------------+---------------+-----------+----------+---------------------------------------------
 id                   | bigint        |           | not null | nextval('inventory_batch_id_seq'::regclass)
 product_id           | bigint        |           | not null |
 list_item_id         | bigint        |           |          |
 purchase_date        | date          |           | not null |
 quantity_purchased   | numeric(12,2) |           | not null |
 purchase_price       | numeric(12,2) |           | not null |
 supplier_id          | bigint        |           |          |
 is_on_sale           | boolean       |           | not null | false
 expiration_date      | date          |           |          |
 created_by_user_id   | bigint        |           |          |
 updated_by_user_id   | bigint        |           |          |
 created_at           | date          |           | not null | now()
 updated_at           | date          |           | not null | now()
 deleted_at           | date          |           |          |
 purchased_by_user_id | bigint        |           |          |
 deleted_by_user_id   | bigint        |           |          |
Indexes:
    "inventory_batch_pkey" PRIMARY KEY, btree (id)
    "ix_inventory_batch_list_item_id" btree (list_item_id)
Foreign-key constraints:
    "fk_inventory_batch_created_by_user_id" FOREIGN KEY (created_by_user_id) REFERENCES users(id)
    "fk_inventory_batch_deleted_by_user_id" FOREIGN KEY (deleted_by_user_id) REFERENCES users(id)
    "fk_inventory_batch_purchased_by_user_id" FOREIGN KEY (purchased_by_user_id) REFERENCES users(id)
    "fk_inventory_batch_supplier_id" FOREIGN KEY (supplier_id) REFERENCES shopping_suppliers(id)
    "fk_inventory_batch_updated_by_user_id" FOREIGN KEY (updated_by_user_id) REFERENCES users(id)
    "inventory_batch_list_item_id_fkey" FOREIGN KEY (list_item_id) REFERENCES shopping_list_items(id)
    "inventory_batch_product_id_fkey" FOREIGN KEY (product_id) REFERENCES shopping_products(id)


family-smart=# \d shopping_group_members
                                          Table "public.shopping_group_members"
      Column      |           Type           | Collation | Nullable |                      Default

------------------+--------------------------+-----------+----------+--------------------------------------------------
--
 id               | integer                  |           | not null | nextval('shopping_group_members_id_seq'::regclass
)
 group_id         | integer                  |           | not null |
 user_id          | integer                  |           | not null |
 role_id          | integer                  |           | not null |
 added_by_user_id | integer                  |           | not null |
 created_at       | timestamp with time zone |           | not null |
 updated_at       | timestamp with time zone |           |          |
 removed_at       | timestamp with time zone |           |          |
Indexes:
    "shopping_group_members_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_group_members_added_by_user_id" btree (added_by_user_id)
    "ix_shopping_group_members_group_id" btree (group_id)
    "ix_shopping_group_members_role_id" btree (role_id)
    "ix_shopping_group_members_user_id" btree (user_id)
    "ux_shopping_group_members_group_user" UNIQUE CONSTRAINT, btree (group_id, user_id)
Foreign-key constraints:
    "shopping_group_members_added_by_user_id_fkey" FOREIGN KEY (added_by_user_id) REFERENCES users(id) ON DELETE CASCAD
E
    "shopping_group_members_group_id_fkey" FOREIGN KEY (group_id) REFERENCES shopping_groups(id) ON DELETE CASCADE
    "shopping_group_members_role_id_fkey" FOREIGN KEY (role_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_group_members_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


family-smart=# \d shopping_groups
                                       Table "public.shopping_groups"
   Column    |           Type           | Collation | Nullable |                   Default
-------------+--------------------------+-----------+----------+---------------------------------------------
 id          | integer                  |           | not null | nextval('shopping_groups_id_seq'::regclass)
 user_id     | integer                  |           | not null |
 name        | character varying(255)   |           | not null |
 description | text                     |           |          |
 status_id   | integer                  |           | not null |
 created_at  | timestamp with time zone |           | not null |
 updated_at  | timestamp with time zone |           |          |
 archived_at | timestamp with time zone |           |          |
 deleted_at  | timestamp with time zone |           |          |
Indexes:
    "shopping_groups_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_groups_status_id" btree (status_id)
    "ix_shopping_groups_user_id" btree (user_id)
Foreign-key constraints:
    "shopping_groups_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_groups_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Referenced by:
    TABLE "shopping_group_members" CONSTRAINT "shopping_group_members_group_id_fkey" FOREIGN KEY (group_id) REFERENCES
shopping_groups(id) ON DELETE CASCADE
    TABLE "shopping_lists" CONSTRAINT "shopping_lists_group_id_fkey" FOREIGN KEY (group_id) REFERENCES shopping_groups(
id) ON DELETE SET NULL


family-smart=# \d shopping_list_items
                                            Table "public.shopping_list_items"
        Column        |           Type           | Collation | Nullable |                     Default

----------------------+--------------------------+-----------+----------+----------------------------------------------
---
 id                   | integer                  |           | not null | nextval('shopping_list_items_id_seq'::regclas
s)
 shopping_list_id     | integer                  |           | not null |
 name_original        | character varying(255)   |           | not null |
 name_normalized      | character varying(255)   |           | not null |
 quantity             | numeric(12,2)            |           |          |
 unit_id              | integer                  |           |          |
 notes                | text                     |           |          |
 status_id            | integer                  |           | not null |
 is_purchased         | boolean                  |           | not null |
 purchased_at         | timestamp with time zone |           |          |
 purchased_by_user_id | integer                  |           |          |
 created_by_user_id   | integer                  |           | not null |
 updated_by_user_id   | integer                  |           |          |
 created_at           | timestamp with time zone |           | not null |
 updated_at           | timestamp with time zone |           |          |
 deleted_at           | timestamp with time zone |           |          |
 product_id           | integer                  |           | not null |
Indexes:
    "shopping_list_items_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_list_items_created_by_user_id" btree (created_by_user_id)
    "ix_shopping_list_items_name_normalized" btree (name_normalized)
    "ix_shopping_list_items_product_id" btree (product_id)
    "ix_shopping_list_items_purchased_by_user_id" btree (purchased_by_user_id)
    "ix_shopping_list_items_shopping_list_id" btree (shopping_list_id)
    "ix_shopping_list_items_status_id" btree (status_id)
    "ix_shopping_list_items_unit_id" btree (unit_id)
    "ix_shopping_list_items_updated_by_user_id" btree (updated_by_user_id)
Foreign-key constraints:
    "fk_shopping_list_items_product" FOREIGN KEY (product_id) REFERENCES shopping_products(id)
    "shopping_list_items_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE RESTR
ICT
    "shopping_list_items_purchased_by_user_id_fkey" FOREIGN KEY (purchased_by_user_id) REFERENCES users(id) ON DELETE S
ET NULL
    "shopping_list_items_shopping_list_id_fkey" FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE
CASCADE
    "shopping_list_items_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_list_items_unit_id_fkey" FOREIGN KEY (unit_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_list_items_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_id) REFERENCES users(id) ON DELETE RESTR
ICT
Referenced by:
    TABLE "inventory_batch" CONSTRAINT "inventory_batch_list_item_id_fkey" FOREIGN KEY (list_item_id) REFERENCES shoppi
ng_list_items(id)
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_shopping_list_item_id_fkey" FOREIGN KEY (shopping_list_item_id)
 REFERENCES shopping_list_items(id) ON DELETE CASCADE


family-smart=# \d shopping_lists
                                        Table "public.shopping_lists"
    Column     |           Type           | Collation | Nullable |                  Default
---------------+--------------------------+-----------+----------+--------------------------------------------
 id            | integer                  |           | not null | nextval('shopping_lists_id_seq'::regclass)
 user_id       | integer                  |           | not null |
 group_id      | integer                  |           |          |
 visibility_id | integer                  |           | not null |
 status_id     | integer                  |           | not null |
 name          | character varying(255)   |           | not null |
 description   | text                     |           |          |
 created_at    | timestamp with time zone |           | not null |
 updated_at    | timestamp with time zone |           |          |
 closed_at     | timestamp with time zone |           |          |
 archived_at   | timestamp with time zone |           |          |
 deleted_at    | timestamp with time zone |           |          |
Indexes:
    "shopping_lists_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_lists_group_id" btree (group_id)
    "ix_shopping_lists_status_id" btree (status_id)
    "ix_shopping_lists_user_id" btree (user_id)
    "ix_shopping_lists_visibility_id" btree (visibility_id)
Foreign-key constraints:
    "shopping_lists_group_id_fkey" FOREIGN KEY (group_id) REFERENCES shopping_groups(id) ON DELETE SET NULL
    "shopping_lists_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_lists_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    "shopping_lists_visibility_id_fkey" FOREIGN KEY (visibility_id) REFERENCES config_codes(id) ON DELETE RESTRICT
Referenced by:
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_shopping_list_id_fkey" FOREIGN KEY (shopping_list_id) R
EFERENCES shopping_lists(id) ON DELETE CASCADE
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_shopping_list_id_fkey" FOREIGN KEY (shopping_list_id) REFERENCE
S shopping_lists(id) ON DELETE CASCADE


family-smart=# \d shopping_prices
                                             Table "public.shopping_prices"
         Column          |           Type           | Collation | Nullable |                   Default

-------------------------+--------------------------+-----------+----------+-------------------------------------------
--
 id                      | integer                  |           | not null | nextval('shopping_prices_id_seq'::regclass
)
 shopping_list_id        | integer                  |           | not null |
 shopping_list_item_id   | integer                  |           | not null |
 product_name_original   | character varying(255)   |           |          |
 product_name_normalized | character varying(255)   |           |          |
 supplier_id             | integer                  |           |          |
 purchase_date           | date                     |           | not null |
 price                   | numeric(10,2)            |           | not null |
 currency_id             | integer                  |           |          |
 offer_flag_id           | integer                  |           |          |
 created_by_user_id      | integer                  |           | not null |
 updated_by_user_id      | integer                  |           |          |
 created_at              | timestamp with time zone |           | not null |
 updated_at              | timestamp with time zone |           |          |
 deleted_at              | timestamp with time zone |           |          |
 product_id              | integer                  |           | not null |
 purchased_by_user_id    | integer                  |           |          |
 expiration_date         | date                     |           |          |
Indexes:
    "shopping_prices_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_prices_created_by_user_id" btree (created_by_user_id)
    "ix_shopping_prices_product_date" btree (product_id, purchase_date DESC)
    "ix_shopping_prices_product_id" btree (product_id)
    "ix_shopping_prices_product_name_normalized" btree (product_name_normalized)
    "ix_shopping_prices_purchase_date" btree (purchase_date)
    "ix_shopping_prices_shopping_list_id" btree (shopping_list_id)
    "ix_shopping_prices_shopping_list_item_id" btree (shopping_list_item_id)
    "ix_shopping_prices_supplier_id" btree (supplier_id)
    "ix_shopping_prices_supplier_product_date" btree (supplier_id, product_id, purchase_date DESC)
    "ix_shopping_prices_updated_by_user_id" btree (updated_by_user_id)
Foreign-key constraints:
    "fk_shopping_prices_product" FOREIGN KEY (product_id) REFERENCES shopping_products(id)
    "fk_shopping_prices_purchased_by_user" FOREIGN KEY (purchased_by_user_id) REFERENCES users(id)
    "shopping_prices_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE RESTRICT
    "shopping_prices_currency_id_fkey" FOREIGN KEY (currency_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_prices_offer_flag_id_fkey" FOREIGN KEY (offer_flag_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_prices_shopping_list_id_fkey" FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE CASC
ADE
    "shopping_prices_shopping_list_item_id_fkey" FOREIGN KEY (shopping_list_item_id) REFERENCES shopping_list_items(id)
 ON DELETE CASCADE
    "shopping_prices_supplier_id_fkey" FOREIGN KEY (supplier_id) REFERENCES shopping_suppliers(id) ON DELETE SET NULL
    "shopping_prices_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_id) REFERENCES users(id) ON DELETE RESTRICT


family-smart=# \d shopping_products
                                    Table "public.shopping_products"
       Column       |           Type           | Collation | Nullable |             Default
--------------------+--------------------------+-----------+----------+----------------------------------
 id                 | integer                  |           | not null | generated by default as identity
 name_normalized    | character varying(255)   |           | not null |
 created_by_user_id | integer                  |           | not null |
 updated_by_user_id | integer                  |           |          |
 created_at         | timestamp with time zone |           | not null | now()
 updated_at         | timestamp with time zone |           |          |
 deleted_at         | timestamp with time zone |           |          |
Indexes:
    "shopping_products_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_products_name_normalized" btree (name_normalized)
    "uq_shopping_products_name_normalized" UNIQUE, btree (name_normalized) WHERE deleted_at IS NULL
Foreign-key constraints:
    "fk_shopping_products_created_by_user" FOREIGN KEY (created_by_user_id) REFERENCES users(id)
    "fk_shopping_products_updated_by_user" FOREIGN KEY (updated_by_user_id) REFERENCES users(id)
Referenced by:
    TABLE "shopping_list_items" CONSTRAINT "fk_shopping_list_items_product" FOREIGN KEY (product_id) REFERENCES shoppin
g_products(id)
    TABLE "shopping_prices" CONSTRAINT "fk_shopping_prices_product" FOREIGN KEY (product_id) REFERENCES shopping_produc
ts(id)
    TABLE "inventory_batch" CONSTRAINT "inventory_batch_product_id_fkey" FOREIGN KEY (product_id) REFERENCES shopping_p
roducts(id)


family-smart=# \d shopping_suppliers
                                           Table "public.shopping_suppliers"
       Column       |           Type           | Collation | Nullable |                    Default
--------------------+--------------------------+-----------+----------+------------------------------------------------
 id                 | integer                  |           | not null | nextval('shopping_suppliers_id_seq'::regclass)
 name               | character varying(255)   |           | not null |
 name_normalized    | character varying(255)   |           | not null |
 status_id          | integer                  |           | not null |
 created_by_user_id | integer                  |           | not null |
 updated_by_user_id | integer                  |           |          |
 created_at         | timestamp with time zone |           | not null |
 updated_at         | timestamp with time zone |           |          |
 deleted_at         | timestamp with time zone |           |          |
Indexes:
    "shopping_suppliers_pkey" PRIMARY KEY, btree (id)
    "ix_shopping_suppliers_created_by_user_id" btree (created_by_user_id)
    "ix_shopping_suppliers_name_normalized" btree (name_normalized)
    "ix_shopping_suppliers_status_id" btree (status_id)
    "ix_shopping_suppliers_updated_by_user_id" btree (updated_by_user_id)
Foreign-key constraints:
    "shopping_suppliers_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE RESTRI
CT
    "shopping_suppliers_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes(id) ON DELETE RESTRICT
    "shopping_suppliers_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_id) REFERENCES users(id) ON DELETE RESTRI
CT
Referenced by:
    TABLE "inventory_batch" CONSTRAINT "fk_inventory_batch_supplier_id" FOREIGN KEY (supplier_id) REFERENCES shopping_s
uppliers(id)
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_supplier_id_fkey" FOREIGN KEY (supplier_id) REFERENCES shopping
_suppliers(id) ON DELETE SET NULL

family-smart=# \d categories
                                    Table "public.categories"
 Column  |         Type          | Collation | Nullable |                Default
---------+-----------------------+-----------+----------+----------------------------------------
 id      | integer               |           | not null | nextval('categories_id_seq'::regclass)
 name    | character varying(50) |           | not null |
 colore  | character varying(7)  |           |          |
 genre   | integer               |           | not null |
 user_id | integer               |           |          |
Indexes:
    "categories_pkey" PRIMARY KEY, btree (id)
    "ix_categories_user_id" btree (user_id)
Foreign-key constraints:
    "categories_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Referenced by:
    TABLE "events" CONSTRAINT "events_category_id_fkey" FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE S
ET NULL
    TABLE "tasks" CONSTRAINT "tasks_category_id_fkey" FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET
 NULL


family-smart=# \d config
                         Table "public.config"
   Column    |          Type          | Collation | Nullable | Default
-------------+------------------------+-----------+----------+---------
 key         | character varying(100) |           | not null |
 value       | text                   |           | not null |
 descrizione | text                   |           |          |
Indexes:
    "config_pkey" PRIMARY KEY, btree (key)


family-smart=# \d config_codes
                                       Table "public.config_codes"
   Column    |           Type           | Collation | Nullable |                 Default
-------------+--------------------------+-----------+----------+------------------------------------------
 id          | integer                  |           | not null | nextval('config_codes_id_seq'::regclass)
 code_type   | character varying(64)    |           | not null |
 code_value  | character varying(64)    |           | not null |
 code_name   | character varying(128)   |           | not null |
 description | text                     |           |          |
 active      | boolean                  |           | not null |
 sort_order  | integer                  |           |          |
 created_at  | timestamp with time zone |           | not null |
 updated_at  | timestamp with time zone |           |          |
Indexes:
    "config_codes_pkey" PRIMARY KEY, btree (id)
    "ix_config_codes_active" btree (active)
    "ix_config_codes_code_type" btree (code_type)
    "ux_config_codes_type_value" UNIQUE CONSTRAINT, btree (code_type, code_value)
Referenced by:
    TABLE "notifications" CONSTRAINT "notifications_notification_type_id_fkey" FOREIGN KEY (notification_type_id) REFER
ENCES config_codes(id) ON DELETE RESTRICT
    TABLE "shared_activity_log" CONSTRAINT "shared_activity_log_action_type_id_fkey" FOREIGN KEY (action_type_id) REFER
ENCES config_codes(id) ON DELETE RESTRICT
    TABLE "shared_activity_log" CONSTRAINT "shared_activity_log_entity_type_id_fkey" FOREIGN KEY (entity_type_id) REFER
ENCES config_codes(id) ON DELETE RESTRICT
    TABLE "shared_activity_log" CONSTRAINT "shared_activity_log_module_code_id_fkey" FOREIGN KEY (module_code_id) REFER
ENCES config_codes(id) ON DELETE RESTRICT
    TABLE "shopping_group_members" CONSTRAINT "shopping_group_members_role_id_fkey" FOREIGN KEY (role_id) REFERENCES co
nfig_codes(id) ON DELETE RESTRICT
    TABLE "shopping_groups" CONSTRAINT "shopping_groups_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes
(id) ON DELETE RESTRICT
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_status_id_fkey" FOREIGN KEY (status_id) REFERENCES conf
ig_codes(id) ON DELETE RESTRICT
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_unit_id_fkey" FOREIGN KEY (unit_id) REFERENCES config_c
odes(id) ON DELETE RESTRICT
    TABLE "shopping_lists" CONSTRAINT "shopping_lists_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config_codes(i
d) ON DELETE RESTRICT
    TABLE "shopping_lists" CONSTRAINT "shopping_lists_visibility_id_fkey" FOREIGN KEY (visibility_id) REFERENCES config
_codes(id) ON DELETE RESTRICT
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_currency_id_fkey" FOREIGN KEY (currency_id) REFERENCES config_c
odes(id) ON DELETE RESTRICT
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_offer_flag_id_fkey" FOREIGN KEY (offer_flag_id) REFERENCES conf
ig_codes(id) ON DELETE RESTRICT
    TABLE "shopping_suppliers" CONSTRAINT "shopping_suppliers_status_id_fkey" FOREIGN KEY (status_id) REFERENCES config
_codes(id) ON DELETE RESTRICT


family-smart=# \d countdowns
                                        Table "public.countdowns"
    Column    |           Type           | Collation | Nullable |                Default
--------------+--------------------------+-----------+----------+----------------------------------------
 id           | integer                  |           | not null | nextval('countdowns_id_seq'::regclass)
 user_id      | integer                  |           | not null |
 title        | character varying(255)   |           | not null |
 target_date  | timestamp with time zone |           | not null |
 status       | character varying(20)    |           | not null | 'active'::character varying
 immagine_url | character varying(1024)  |           |          |
 created_at   | timestamp with time zone |           | not null |
 updated_at   | timestamp with time zone |           |          |
 closed_at    | timestamp with time zone |           |          |
 reopened_at  | timestamp with time zone |           |          |
Indexes:
    "countdowns_pkey" PRIMARY KEY, btree (id)
    "ix_countdowns_user_id" btree (user_id)
    "ix_countdowns_user_status" btree (user_id, status)
    "ix_countdowns_user_target_date" btree (user_id, target_date)
Check constraints:
    "ck_countdowns_status_valid" CHECK (status::text = ANY (ARRAY['active'::character varying, 'closed'::character vary
ing]::text[]))
Foreign-key constraints:
    "countdowns_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


family-smart=# \d daily_entries
                                         Table "public.daily_entries"
      Column      |          Type           | Collation | Nullable |                  Default
------------------+-------------------------+-----------+----------+-------------------------------------------
 id               | integer                 |           | not null | nextval('daily_entries_id_seq'::regclass)
 user_id          | integer                 |           | not null |
 data_riferimento | date                    |           | not null |
 tipo             | character varying(20)   |           | not null |
 testo            | text                    |           | not null |
 immagine_url     | character varying(1024) |           |          |
Indexes:
    "daily_entries_pkey" PRIMARY KEY, btree (id)
    "ix_daily_entries_user_data" btree (user_id, data_riferimento)
    "ix_daily_entries_user_tipo_data" btree (user_id, tipo, data_riferimento)
    "ux_daily_entries_one_goal_per_day" UNIQUE, btree (user_id, data_riferimento) WHERE tipo::text = 'OD'::text
    "ux_daily_entries_one_monthly_goal" UNIQUE, btree (user_id, data_riferimento) WHERE tipo::text = 'OM'::text
    "ux_daily_entries_one_weekly_goal" UNIQUE, btree (user_id, data_riferimento) WHERE tipo::text = 'OW'::text
Check constraints:
    "ck_daily_entries_tipo_valid" CHECK (tipo::text = ANY (ARRAY['OD'::character varying, 'PD'::character varying, 'N1'
::character varying, 'N2'::character varying, 'N3'::character varying, 'N4'::character varying, 'OW'::character varying
, 'PW'::character varying, 'OM'::character varying, 'PM'::character varying, 'EP'::character varying, 'EN'::character v
arying]::text[]))
Foreign-key constraints:
    "daily_entries_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


family-smart=# \d events
                                         Table "public.events"
     Column      |           Type           | Collation | Nullable |              Default
-----------------+--------------------------+-----------+----------+------------------------------------
 id              | integer                  |           | not null | nextval('events_id_seq'::regclass)
 titolo          | character varying(255)   |           | not null |
 descrizione     | text                     |           |          |
 data_inizio     | timestamp with time zone |           | not null |
 data_fine       | timestamp with time zone |           |          |
 tutto_il_giorno | boolean                  |           | not null |
 luogo           | character varying(255)   |           |          |
 category_id     | integer                  |           |          |
 user_id         | integer                  |           | not null |
 rrule           | character varying(255)   |           |          |
Indexes:
    "events_pkey" PRIMARY KEY, btree (id)
    "ix_events_data_inizio" btree (data_inizio)
    "ix_events_user_id" btree (user_id)
Foreign-key constraints:
    "events_category_id_fkey" FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    "events_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


family-smart=# \d habit_log
                                 Table "public.habit_log"
      Column      |  Type   | Collation | Nullable |                Default
------------------+---------+-----------+----------+---------------------------------------
 id               | integer |           | not null | nextval('habit_log_id_seq'::regclass)
 habit_id         | integer |           | not null |
 data_riferimento | date    |           | not null |
 count            | integer |           | not null | 1
Indexes:
    "habit_log_pkey" PRIMARY KEY, btree (id)
    "idx_habit_log_habit_date" btree (habit_id, data_riferimento)
    "uix_habit_log_date" UNIQUE CONSTRAINT, btree (habit_id, data_riferimento)
Foreign-key constraints:
    "habit_log_habit_id_fkey" FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE


family-smart=# \d habit_period
                               Table "public.habit_period"
   Column    |  Type   | Collation | Nullable |                 Default
-------------+---------+-----------+----------+------------------------------------------
 id          | integer |           | not null | nextval('habit_period_id_seq'::regclass)
 habit_id    | integer |           | not null |
 data_inizio | date    |           | not null |
 data_fine   | date    |           |          |
 target      | integer |           | not null | 1
Indexes:
    "habit_period_pkey" PRIMARY KEY, btree (id)
    "idx_habit_period_habit_data_inizio" btree (habit_id, data_inizio)
    "idx_habit_period_habit_id" btree (habit_id)
Foreign-key constraints:
    "habit_period_habit_id_fkey" FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE


family-smart=# \d habits
                                       Table "public.habits"
    Column    |          Type           | Collation | Nullable |              Default
--------------+-------------------------+-----------+----------+------------------------------------
 id           | integer                 |           | not null | nextval('habits_id_seq'::regclass)
 user_id      | integer                 |           | not null |
 titolo       | character varying(255)  |           | not null |
 tipo         | character varying(1)    |           | not null |
 rrule        | character varying(255)  |           |          |
 immagine_url | character varying(1024) |           |          |
Indexes:
    "habits_pkey" PRIMARY KEY, btree (id)
    "idx_habits_user" btree (user_id)
Foreign-key constraints:
    "habits_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Referenced by:
    TABLE "habit_log" CONSTRAINT "habit_log_habit_id_fkey" FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCA
DE
    TABLE "habit_period" CONSTRAINT "habit_period_habit_id_fkey" FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE
 CASCADE


family-smart=# \d notifications
                                            Table "public.notifications"
        Column        |           Type           | Collation | Nullable |                  Default
----------------------+--------------------------+-----------+----------+-------------------------------------------
 id                   | integer                  |           | not null | nextval('notifications_id_seq'::regclass)
 user_id              | integer                  |           | not null |
 notification_type_id | integer                  |           | not null |
 title                | character varying(255)   |           | not null |
 message              | text                     |           | not null |
 read_at              | timestamp with time zone |           |          |
 created_at           | timestamp with time zone |           | not null |
 updated_at           | timestamp with time zone |           |          |
 deleted_at           | timestamp with time zone |           |          |
Indexes:
    "notifications_pkey" PRIMARY KEY, btree (id)
    "ix_notifications_notification_type_id" btree (notification_type_id)
    "ix_notifications_user_id" btree (user_id)
Foreign-key constraints:
    "notifications_notification_type_id_fkey" FOREIGN KEY (notification_type_id) REFERENCES config_codes(id) ON DELETE
RESTRICT
    "notifications_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE


family-smart=# \d shared_activity_log
                                            Table "public.shared_activity_log"
        Column        |           Type           | Collation | Nullable |                     Default

----------------------+--------------------------+-----------+----------+----------------------------------------------
---
 id                   | integer                  |           | not null | nextval('shared_activity_log_id_seq'::regclas
s)
 module_code_id       | integer                  |           | not null |
 entity_type_id       | integer                  |           | not null |
 action_type_id       | integer                  |           | not null |
 entity_id            | character varying(128)   |           | not null |
 performed_by_user_id | integer                  |           | not null |
 created_at           | timestamp with time zone |           | not null |
 payload_before       | text                     |           |          |
 payload_after        | text                     |           |          |
Indexes:
    "shared_activity_log_pkey" PRIMARY KEY, btree (id)
    "ix_shared_activity_log_action_type_id" btree (action_type_id)
    "ix_shared_activity_log_created_at" btree (created_at)
    "ix_shared_activity_log_entity" btree (module_code_id, entity_type_id, entity_id)
    "ix_shared_activity_log_entity_id" btree (entity_id)
    "ix_shared_activity_log_entity_type_id" btree (entity_type_id)
    "ix_shared_activity_log_module_code_id" btree (module_code_id)
    "ix_shared_activity_log_performed_by_user_id" btree (performed_by_user_id)
Foreign-key constraints:
    "shared_activity_log_action_type_id_fkey" FOREIGN KEY (action_type_id) REFERENCES config_codes(id) ON DELETE RESTRI
CT
    "shared_activity_log_entity_type_id_fkey" FOREIGN KEY (entity_type_id) REFERENCES config_codes(id) ON DELETE RESTRI
CT
    "shared_activity_log_module_code_id_fkey" FOREIGN KEY (module_code_id) REFERENCES config_codes(id) ON DELETE RESTRI
CT
    "shared_activity_log_performed_by_user_id_fkey" FOREIGN KEY (performed_by_user_id) REFERENCES users(id) ON DELETE R
ESTRICT


family-smart=# \d tasks
                                        Table "public.tasks"
    Column     |           Type           | Collation | Nullable |              Default
---------------+--------------------------+-----------+----------+-----------------------------------
 id            | integer                  |           | not null | nextval('tasks_id_seq'::regclass)
 titolo        | character varying(255)   |           | not null |
 descrizione   | text                     |           |          |
 data_start    | timestamp with time zone |           | not null |
 data_scadenza | timestamp with time zone |           |          |
 priorita      | character varying(10)    |           | not null |
 luogo         | character varying(255)   |           |          |
 fatto         | boolean                  |           | not null |
 data_fatto    | timestamp with time zone |           |          |
 category_id   | integer                  |           |          |
 user_id       | integer                  |           | not null |
 parent_id     | integer                  |           |          |
Indexes:
    "tasks_pkey" PRIMARY KEY, btree (id)
    "ix_tasks_parent_id" btree (parent_id)
    "ix_tasks_user_id" btree (user_id)
Foreign-key constraints:
    "tasks_category_id_fkey" FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    "tasks_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
    "tasks_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Referenced by:
    TABLE "tasks" CONSTRAINT "tasks_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE


family-smart=# \d users
                                             Table "public.users"
         Column         |           Type           | Collation | Nullable |              Default
------------------------+--------------------------+-----------+----------+-----------------------------------
 id                     | integer                  |           | not null | nextval('users_id_seq'::regclass)
 username               | character varying(50)    |           | not null |
 email                  | character varying(100)   |           | not null |
 password_hash          | character varying(255)   |           | not null |
 max_subtask_depth_user | integer                  |           |          |
 is_superuser           | boolean                  |           | not null | false
 must_change_password   | boolean                  |           | not null | true
 deleted_at             | timestamp with time zone |           |          |
 deleted_by_user_id     | integer                  |           |          |
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "ix_users_deleted_at" btree (deleted_at)
    "ix_users_email" btree (email)
    "ix_users_username" btree (username)
    "uq_users_email_lower" UNIQUE, btree (lower(email::text))
    "uq_users_username_lower" UNIQUE, btree (lower(username::text))
Foreign-key constraints:
    "fk_users_deleted_by_user_id" FOREIGN KEY (deleted_by_user_id) REFERENCES users(id) ON DELETE SET NULL
Referenced by:
    TABLE "categories" CONSTRAINT "categories_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCAD
E
    TABLE "countdowns" CONSTRAINT "countdowns_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCAD
E
    TABLE "daily_entries" CONSTRAINT "daily_entries_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE
CASCADE
    TABLE "events" CONSTRAINT "events_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "inventory_batch" CONSTRAINT "fk_inventory_batch_created_by_user_id" FOREIGN KEY (created_by_user_id) REFEREN
CES users(id)
    TABLE "inventory_batch" CONSTRAINT "fk_inventory_batch_deleted_by_user_id" FOREIGN KEY (deleted_by_user_id) REFEREN
CES users(id)
    TABLE "inventory_batch" CONSTRAINT "fk_inventory_batch_purchased_by_user_id" FOREIGN KEY (purchased_by_user_id) REF
ERENCES users(id)
    TABLE "inventory_batch" CONSTRAINT "fk_inventory_batch_updated_by_user_id" FOREIGN KEY (updated_by_user_id) REFEREN
CES users(id)
    TABLE "shopping_prices" CONSTRAINT "fk_shopping_prices_purchased_by_user" FOREIGN KEY (purchased_by_user_id) REFERE
NCES users(id)
    TABLE "shopping_products" CONSTRAINT "fk_shopping_products_created_by_user" FOREIGN KEY (created_by_user_id) REFERE
NCES users(id)
    TABLE "shopping_products" CONSTRAINT "fk_shopping_products_updated_by_user" FOREIGN KEY (updated_by_user_id) REFERE
NCES users(id)
    TABLE "users" CONSTRAINT "fk_users_deleted_by_user_id" FOREIGN KEY (deleted_by_user_id) REFERENCES users(id) ON DEL
ETE SET NULL
    TABLE "habits" CONSTRAINT "habits_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "notifications" CONSTRAINT "notifications_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE
CASCADE
    TABLE "shared_activity_log" CONSTRAINT "shared_activity_log_performed_by_user_id_fkey" FOREIGN KEY (performed_by_us
er_id) REFERENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_group_members" CONSTRAINT "shopping_group_members_added_by_user_id_fkey" FOREIGN KEY (added_by_user
_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "shopping_group_members" CONSTRAINT "shopping_group_members_user_id_fkey" FOREIGN KEY (user_id) REFERENCES us
ers(id) ON DELETE CASCADE
    TABLE "shopping_groups" CONSTRAINT "shopping_groups_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DEL
ETE CASCADE
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_created_by_user_id_fkey" FOREIGN KEY (created_by_user_i
d) REFERENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_purchased_by_user_id_fkey" FOREIGN KEY (purchased_by_us
er_id) REFERENCES users(id) ON DELETE SET NULL
    TABLE "shopping_list_items" CONSTRAINT "shopping_list_items_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_i
d) REFERENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_lists" CONSTRAINT "shopping_lists_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELET
E CASCADE
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id) REFER
ENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_prices" CONSTRAINT "shopping_prices_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_id) REFER
ENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_suppliers" CONSTRAINT "shopping_suppliers_created_by_user_id_fkey" FOREIGN KEY (created_by_user_id)
 REFERENCES users(id) ON DELETE RESTRICT
    TABLE "shopping_suppliers" CONSTRAINT "shopping_suppliers_updated_by_user_id_fkey" FOREIGN KEY (updated_by_user_id)
 REFERENCES users(id) ON DELETE RESTRICT
    TABLE "tasks" CONSTRAINT "tasks_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
