# Copyright 2020 Newcastle University.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mobiliseclient import *
import data_warehouse
import participant_loader_from_esc
import warehouse_loader_from_esc
import mobilise_load_fns

hostname = "mobilised.di-projects.net"
port = 443
ssl = True

# Log onto the system and obtain a JWT
mc = EscClient(hostname, port, ssl)
# print('Issuing')
# jwt = tc.issueToken("username", "password", "Python Test")
# The actual token is a field of the returned jwt object
# token = jwt.token

# Use an existing JWT
token = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1NSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNjI2MzQ5ODU4LCJpYXQiOjE1OTQ4MTM4NTgsImp0aSI6IjJjOWZhZmU1NzMwZjZkZGMwMTczNTI1MDQwZmYzYjBhIn0.YLOQhgHrcKuGBiCLUEiDHNA74666-dDwgNSD6FHdD03UkW2tUoMwJAsgAaYKa6PBZfBy95vHB4XrPcXDhyfCtA'
mc.jwt = token

# Use this to validate a token that you already have
print('Validating')
print(mc.validateToken(token))

# Create a connection to the data warehouse
data_warehouse = data_warehouse.DataWarehouse("db-credentials.json", "datawarehouse")

# example 1
study_id = 4

# Find a project in e-Science Central by ID
esc_project = "BB001"
project = mc.getProjectByStudyCode(esc_project)

esc_parts = participant_loader_from_esc.get_all_participants_in_esc_study(mc, project.id)
print("Participants in e-Science Central")
for p in esc_parts:
    print(p)

dw_parts = participant_loader_from_esc.get_all_participants_in_dw_study(data_warehouse, study_id)
print("Participants in Data Warehouse")
for p in dw_parts:
    print(p)

print("New Participants")
new_parts = participant_loader_from_esc.list_difference(esc_parts, dw_parts)
for p in new_parts:
    print(p)

new_participants = participant_loader_from_esc.insert_new_participants_in_warehouse(mc, data_warehouse,
                                                                                    project.id, study_id)
print("Inserted Participants")
for p in new_participants:
    print(p)

dw_participants = participant_loader_from_esc.get_all_participants_in_dw_study(data_warehouse, study_id)
print("Participants now in the DW")
for p in dw_participants:
    print(p)

events = warehouse_loader_from_esc.extract_events_from_esc(mc, esc_project)
for e in events:
    print(e)

# find unique types of data:
# event_types = warehouse_loader_from_esc.get_data_types_from_esc(mc, esc_project)
# print("All Event Types")
# for e in event_types:
#    print(e)

# print all mapper functions
print("All Mapper Functions")
for f in mobilise_load_fns.fn_mapper().keys():
    print(f)

unique_id_measurement_type = 220  # the measurement type that holds the unique id for each measurement group

print("Load Data from e-Science Central into Data Warehouse")
new_instances = warehouse_loader_from_esc.load_dw_from_esc( mc, data_warehouse, study_id, esc_project,
                                                            unique_id_measurement_type, mobilise_load_fns.fn_mapper())
print(*new_instances, sep='\n')