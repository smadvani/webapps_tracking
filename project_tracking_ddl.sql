-- 	project_tracking_ddl.sql
--
--	PURPOSE:  create pilot (sqlite) database for unified project tracking tool 
--
--	NOTES:
--		1) based on current Excel baseed sheet G. Montgomery uses now for tracking
--		2) find all integer PRIMARY KEY as set to serial PRIMARY KEY if moves to postgres

--		 
--
--
--	AUTHOR(S):
--		Sanjay Advani, USGS (SA)
--
--	HISTORY:
--==========================================================================
--	2016-11-25: Created. SA.
--	2016-12-06: Added view for hours report. SA.
--	2016-12-09:	Split out fixed rates to sytems and project management and from federal SA.
--				Added hosting costs. SA
--	2016-12-13: Added taks order to the project plan and project actuals.  Assume all work can be place in task order
--					OR - that a task order can be "dummied" for reserve funds
--==========================================================================

--==========================================================================
-- uncomment for postgres or other db.  Spatialite or SQLite run in command line.
--create database project_track
--;
--set owner once log in roles are defined in hosted env.
-- alter database project_track
	-- owner = XXXX
	-- ;
--===============================
-- CREATE sqlite3 DATABASE IN 
--	COMMAND LIND

-- open sqlite in command line and open or create project_track.db with:
--     "sqlite3.exe project_track.db"
-- 
--
--===============================
-- CREATE TABLES
-- run with:
-- .read H:/01_ISB/PlanningTools/project_tracking_ddl.sql
--===============================
drop table if exists role;
create table role
	(
	 role_type character varying (8) PRIMARY KEY,
	 role_description character varying (25)
	 )
;

drop table if exists personnel;
create table personnel
	(
	 personnel_id integer PRIMARY KEY,
	 last_name character varying (25),
	 first_name character varying (25),
	 affiliation character varying (25),
	 role character varying (8)
	)
;

drop table if exists agency;
create table agency
	(
	 agency_code character varying(8) PRIMARY KEY,
	 agency_descr character varying (50),
	 agency_type character varying (8)
	)
;

drop table if exists project;
create table project
	(
	 project_code character varying(8) PRIMARY KEY,
	 project_full_name character varying(50),
	 primary_inves integer,
	 pm integer,
	 start_year integer,
	 time_horizon integer, -- years for which this project is initially funded
	 funds_transferred integer -- change to boolean for non lite implementation
	 )
	;
	
drop table if exists project_plan;
create table project_plan
	(
	 project_code character varying(8),
	 task_order character varying (24),
	 fiscal_year integer,
	 agency_code character varying(8),
	 gross_funds real,
	 overhead_rate real,
	 fixed_pm_rate real,
	 fixed_sys_rate real,
	 fed_rate real,
	 hosting real,
	 avail_for_dev real,
	 assumed_dev_hrly real,
	 planned_hrs integer,
	 assumptions character varying,
	 PRIMARY KEY (project_code, task_order, fiscal_year, agency_code) 
	)
;

drop table if exists project_actuals;
create table project_actuals
	(
	 project_code character varying(8),
	 task_order character varying (24),
	 fiscal_year integer,
	 agency_code character varying(8),
	 work_month integer,
	 actual_hrs real,
	 actual_rate real,
	 PRIMARY KEY (project_code, task_order, fiscal_year, agency_code, work_month) 
	)
;

-- POPULATE TABLES
insert into personnel (last_name, first_name, affiliation, role)

select  'Advani', 'Sanjay', 'USGS', 'PI'  union all
select  'Montgomery', 'Gail', 'USGS', 'PI'  union all
select  'Kern', 'Tim', 'USGS', 'PI'  union all
select  'Brown', 'Don', 'USGS', 'PI'  union all
select  'Long', 'Dell', 'USGS', 'PI'  union all
select  'Fisher', 'Chariti', 'CNT', 'PM'  union all
select  'Schweizer', 'Haylee', 'CNT', 'PM'  union all
select  'Eberhardt Frank', 'Megan', 'CNT', 'PM' 
;

insert into agency (agency_code, agency_descr,agency_type)
select  'BLM', 'DOI Bureau of Land Management', 'Federal'  union all
select  'FWS', 'DOI Fish and Wildlife Service', 'Federal'  union all
select  'NPS', 'DOI National Park Service', 'Federal'  union all
select  'FLH', 'Federal Land Highways', 'Federal'  union all
select  'CSU', 'Colorado State University', 'EDU' union all
select 'FORT', 'Fort Base funds', 'Federal'
;


-- CREATE VIEWS
drop view if exists vw_hrs_rpt;
create view vw_hrs_rpt as
select act.project_code as project_code, act.fiscal_year as fiscal_year, act.task_order as task_order, act.agency_code as agency_code, 
      sum(case when work_month = 1 then actual_hrs else 0 end) as jan,
      sum(case when work_month = 2 then actual_hrs else 0 end) as feb,
      sum(case when work_month = 3 then actual_hrs else 0 end) as mar,
      sum(case when work_month = 4 then actual_hrs else 0 end) as apr,
      sum(case when work_month = 5 then actual_hrs else 0 end) as may,
      sum(case when work_month = 6 then actual_hrs else 0 end) as jun,
      sum(case when work_month = 7 then actual_hrs else 0 end) as jul,
      sum(case when work_month = 8 then actual_hrs else 0 end) as aug,
      sum(case when work_month = 9 then actual_hrs else 0 end) as sep,
      sum(case when work_month = 10 then actual_hrs else 0 end) as oct,
      sum(case when work_month = 11 then actual_hrs else 0 end) as nov,
      sum(case when work_month = 12 then actual_hrs else 0 end) as dec,
	  sum(work_month) as yr_tot,
	  sum(actual_hrs)
from project_actuals as act
group by project_code, fiscal_year, agency_code
order by project_code, fiscal_year, agency_code
;
-- FOR TESTING VIEW
-- insert into project_actuals (project_code, task_order, fiscal_year, agency_code, work_month, actual_hrs, actual_rate)
-- select 'PRIS', 'ABCXYZ', 2016, 'BLM', 1, 17, 70 union all
-- select 'PRIS', 'ABCXYZ',2016, 'BLM', 2, 20, 70 union all
--select 'PRIS', 'ABCXYZ',2016, 'BLM', 2, 15, 78 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 3, 8, 78 union all
-- select 'PRIS', 'ABCXYZ',2016, 'BLM', 4, 15, 70 union all
-- select 'PRIS', 'ABCXYZ',2016, 'BLM', 6, 12, 75 union all
--select 'PRIS', 'ABCXYZ',2016, 'BLM', 6, 15, 78 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 7, 17, 70 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 8, 20, 70 union all
--select 'PRIS','ABCXYZ', 2016, 'BLM', 8, 5, 90 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 9, 5, 70 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 10, 20, 70 union all
--select 'PRIS','ABCXYZ', 2016, 'BLM', 10, 12, 78 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 11, 17, 70 union all
-- select 'PRIS','ABCXYZ', 2016, 'BLM', 12, 17, 70 union all
-- select 'WHB', 'ABCXYZ',2016, 'FORT', 1, 5, 70 union all
-- select 'WHB', 'COMZZZ', 2016, 'FORT', 2, 50, 70 union all
-- select 'WHB', 'COMZZZ',2016, 'FORT', 2, 5, 78 union all
-- select 'WHB', 'COMZZZ',2016, 'FORT', 3, 18, 78 union all
-- select 'WHB', 'COMZZZ',2016, 'FORT', 4, 5, 70 union all
-- select 'WHB','COMZZZ', 2016, 'FORT', 6, 2, 75 union all
-- select 'WHB','COMZZZ', 2016, 'FORT', 6, 5, 78 union all
-- select 'WHB', 'COMZZZ',2016, 'FORT', 7, 7, 70 union all
-- select 'WHB', 'COMZZZ', 2016, 'FORT', 8, 20, 70 union all
-- select 'WHB', 'COMZZZ', 2016, 'FORT', 8, 6, 90 union all
-- select 'WHB', 'COMZZZ', 2016, 'FORT', 11, 2, 70 union all
-- select 'WHB', 'COMZZZ', 2016, 'FORT', 12, 1, 70
-- ;
