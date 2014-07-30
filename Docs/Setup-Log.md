Setup Log
============

Steps about how to build the database and service.


## Get Line Info    
Use `../Crawlers/Basic/get_line_info.py` to retrieve raw data stored in `../Data/External/` as `lines-*.json`. Since the data may vary, it should be re-run in different times of the day.    
It contains basic information for all lines:        

| Property       | Note             | Example                          |
| :------------- | :--------------- | :------------------------------- |
| line_guid | Unique identity of the line in guid | 9f1f41ea-8939-492b-a969-028ef588857b |
| line_name | Display name | 128 |
| line_direction | Direction of the line, usually last station | 钟南街首末站西=>车坊首末站 |


## Get Route Info
Use `../Crawlers/Basic/run_line_route.sh` to retrieve raw data stored in `../Data/External/` as `line_*.txt`. For route info of the lines to be retrieved, their guid and name should be written in `../Crawlers/Basic/run_line_route.sh`.    
It contains details of the routes:        

| Property       | Note             | Example                          |
| :------------- | :--------------- | :------------------------------- |
| SCode | Unique identity code of the station | KFN |
| SName | Display name | 创意产业园 | 
| BusInfo | License plate number of the | 苏E-64713 |
| InTime | Latest arrival time of the bus | 21:04:15 | 


## Merge Line Data & Get Station Info
1. Firstly, use `../Import/merge_line_info.py` to extract line info from raw data in `../Data/External/`.       
2. Secondly, use `../Import/merge_line_route.py` to extract route info from raw data in `../Data/External/`.       
3. Thirdly, use `../Import/merge_station_info.py` to filter out a station code and name list from the results in previous steps.        
4. Finally, use `../Crawlers/Basic/get_station_detail.py` with the list to retrieve `../Data/External/station_detail.json`.        

It contains details of the stations:        

| Property       | Note             | Example                          |
| :------------- | :--------------- | :------------------------------- |
| NoteGuid | Unique identity code of the station  | EGT  | 
| Name | Display name  | 翰林邻里中心  | 
| Direct | On which side of the road  | 西  | 
| Canton | District part in its address  | 工业园区  | 
| Road | Road part in its address  | 林泉街  | 
| Sect | Cross road nearby  | 仁爱路-文景街  | 


## Merge Station Data
In previous steps, `../Import/Merged/line_info.json` and `../Import/Merged/line_route.json` have already been generated. Now, use `../Import/merge_station_detail.py` to extract station and save in `../Import/Merged/station_all.json`.        

It contains refined details of the stations:        
    
| Property       | Note             | Example                          |
| :------------- | :--------------- | :------------------------------- |
| code | Unique identity code of the station  | EGT  | 
| name | Display name  | 翰林邻里中心  | 
| geo_side | On which side of the road  | 西  | 
| geo_road | Address of the station  | 工业园区林泉街近仁爱路-文景街交叉口处  | 


## Merge Internal Data

Use `../Import/merge_geo.py` with internal data to generate `../Import/Merged/geo_line.json` and `../Import/Merged/geo_station.json`.        

It contains all the raw data of Line/Bus required in `../Docs/Database-Design.md`.


## Build the Database With Line & Station Data

Use `../Import/build_database.py` along with `../Import/Merged/geo_line.json` and `../Import/Merged/geo_station.json` which were just generated. 

