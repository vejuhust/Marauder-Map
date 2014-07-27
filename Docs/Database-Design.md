Database Design
============

We use a graph database, [Neoj4](http://www.neo4j.org), in this project to adapt our needs for real-time transit info.


Nodes
------------

### Summary

* Line
* Bus
* Station


### Line

__Line__ represents bus routes, the same route with different directions should be treated as different lines.

| Property       | Type             | Note                          |
| :------------- | :--------------- | :---------------------------- |
| __guid__       | string           | unique identity in guid       |
| sibling*       | line.guid        | guid of the same route with opposite direction |
| name           | string           | display name                  |
| direction      | string           | usually last station          |
| is_active      | boolean          | is it available now           |
| shape_lat      | double [ ]       | latitude of shape points      |
| shape_long     | double [ ]       | longitude of shape points     |
| shape_dist     | double [ ]       | distance traveled along shapes from the first shape point |
| shape_station  | string [ ]       | station code if the point is a station, or empty |
| station        | station.id [ ]   | id of stations on the route   |
| bus*           | bus.tag [ ]      | plate number of buses on the route |

> N.B.    
> __unique identity__ means unique identity of the nodes.     
> asterisk* means it might not be stored explicitly because it can be calculated from other data stored.     


### Bus

__Bus__ represents buses, it might service in different __lines__ at different time.

| Property       | Type             | Note                          |
| :------------- | :--------------- | :---------------------------- |
| __tag__        | string           | license plate number of the bus |
| arrival_time   | datetime         | latest arrival time recorded  |
| arrival_station | station.id      | id of latest arrival station recorded |
| arrival_line   | line.guid        | guid of the line it serves in latest arrival record |
| history_time   | datetime [ ]     | history of arrival_time       |
| history_station | station.id [ ]  | history of arrival_station    |
| history_line   | line.guid [ ]    | history of arrival_line       |
| next_station*  | station.id       | id of next station on the route |
| eta_duration*  | datetime         | estimated time (duration) of arrival |


### Station

__Station__ represents bus stops on a __line__.

| Property       | Type             | Note                          |
| :------------- | :--------------- | :---------------------------- |
| __code__       | string           | unique identity code          |
| name           | string           | display name                  |
| sibling*       | station.code     | code of station on the other side of the road |
| geo_road       | string           | road in its address           |
| geo_side       | string           | on which side of the road     |
| geo_lat        | double           | latitude of the station       |
| geo_long       | double           | longitude of the station      |
| line*          | line.guid [ ]    | guid of lines contain the station | 



Relationships
------------

### Summary

| From           | To             | Name            |
| :------------- | -------------: | :-------------: |
| Line           | Line           | Sibling Line    |
| Line           | Station        | Contain         |
| Bus            | Line           | Serve As        |
| Bus            | Station        | Stop At         |
| Station        | Station        | Connect         |
| Station        | Station        | Sibling Station |

