DROP TABLE IF EXISTS robert.local_demand_index;

CREATE TABLE robert.local_demand_index AS
SELECT
      demand_index.dim_location
    , nodes.center_lat AS lat
    , nodes.center_lng AS long
    , nodes.dim_city AS dim_city
    , nodes.dim_market AS dim_market
    , demand_index.searches
    , demand_index.viewers
    , demand_index.contacts
    , demand_index.requests
    , ds_night
FROM (
    SELECT
        dim_location
      , ds_night
      , AVG(searches_index) AS searches
      , AVG(viewers_index) AS viewers
      , AVG(contacts_index) AS contacts
      , AVG(requests_index) AS requests
    FROM pricing.local_demand_index
    WHERE ds_night >= '2016-10-03' AND ds_night <= '2017-10-04'
    GROUP BY
          dim_location
        , ds_night
) demand_index
JOIN (
    SELECT DISTINCT
        node_id
      , dim_market
      , dim_city
      , center_lat
      , center_lng
FROM pricing.kdtree_node_1k_market
WHERE ds = '2016-07-31' AND
      model = '2016-07-20' AND
      dim_market not like '%Other%'
) nodes
ON demand_index.dim_location = CAST(nodes.node_id AS VARCHAR)
;
