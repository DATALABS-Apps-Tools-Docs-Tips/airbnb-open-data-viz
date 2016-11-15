DROP TABLE IF EXISTS robert.local_demand_index;

CREATE TABLE robert.local_demand_index AS
SELECT
      demand_index.dim_location
    , top_nodes.center_lat AS lat
    , top_nodes.center_lng AS long
    , top_nodes.dim_market AS dim_market
    , demand_index.searches
    , demand_index.requests
    , ds_night
FROM (
    SELECT
        dim_location
      , ds_night
      , searches_index AS searches
      , requests_index AS requests
    FROM 
      pricing.local_demand_index
    WHERE 
      ds_night >= '2016-11-15' AND 
      ds_night <= '2017-01-10' AND
      ds = '2016-11-12'
) demand_index
JOIN (
    SELECT
        node_id
      , dim_market
      , dim_city
      , center_lat
      , center_lng
    FROM (
        SELECT
            node_id
          , dim_market
          , dim_city
          , sub_listing_count
          , center_lat
          , center_lng
          , rank() over (partition by node_id order by sub_listing_count desc) as rk
        FROM 
          pricing.kdtree_node_1k_market
        WHERE 
          ds = '2016-11-13' AND
          model = '2016-07-20' AND
          dim_market not like '%Other%'
    ) nodes
    WHERE
      rk = 1 AND sub_listing_count >= 10
) top_nodes
ON demand_index.dim_location = CAST(top_nodes.node_id AS VARCHAR)
;
