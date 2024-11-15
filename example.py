#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import regex as re
import math
import gantt
import sys

import logging
gantt.init_log_to_sysout(level=logging.CRITICAL)

colors=["#FFFF90", "#90FFA6", "#90D3FF", "#D390FF", "#FF9090"]
# Format 
# [TIME] [CCSD_PROFILE] [WORKER_#_TASKNAME(_#id_#subtaskID)_START(or END)]
worker_list=[]
items = []
flag = 1
if len(sys.argv) > 1:
    flag = sys.argv[1]

f = open("sample.txt", 'r')
lines = f.readlines()

for line in lines:
    line = re.sub('\[\s+', '[', line)
    #print(line)
    line = line.split()
    #print(line)
    if len(line) == 3:
        if line[1] == "[CCSD_PROFILE]":
            words = line[2].split('_')
            if len(words) > 3:
                #print(words)
                if words[len(words) - 1] == 'START':
                    task_type = words[0]
                    worker_name = words[0] + '_' + words[1]
                    if worker_name not in worker_list:
                        worker_list.append(worker_name)

                    idx = line[0].find(']')
                    time = line[0][1:idx]

                    task_id = 0
                    task_name = 'T' # words[2]
                    if len(words) > 5:
                        task_name = task_name + '_' + words[3] + '_' + words[4]
                        task_id = int(words[3]) + 1
                    if ((int(flag) == 1) or ((len(words) > 5)) and (task_type != 'SCHD')):
                        items.append({'task_type':task_type, 'worker_name':worker_name, 'task_id':task_id, 'task_name':task_name, 'start':time, 'end':0})
                if words[len(words) - 1] == 'END':
                    task_type = words[0]
                    worker_name = words[0] + '_' + words[1]
                    task_name = 'T' # words[2]
                    if len(words) > 5:
                        task_name = task_name + '_' + words[3] + '_' + words[4]
                        
                    if worker_name not in worker_list:
                        worker_list.append(worker_name)

                    idx = line[0].find(']')
                    time = line[0][1:idx]

                    for item in items[::-1]:
                        if item['task_type'] == task_type and item['task_name'] == task_name and item['end'] == 0:
                            item['end'] = time
                            break
f.close()

# Change font default
gantt.define_font_attributes(fill='black', stroke='black', stroke_width=0, font_family="Verdana")

#print("len : ", len(items))
start_time = float(items[0]['start'])
end_time = float(items[len(items) - 1]['end'])
#print(start_time)
#print(end_time)

worker_object = []
for worker in worker_list:
    p = gantt.Project(name=worker)
    worker_object.append({'name':worker, 'object':p})
#print(worker_list)
p = gantt.Project(name='CCSD')
time_scale = 5   # 1칸에 1ms (100) , 1칸에 1us (0.1)

min = 0xffffffff
for item in items:
    if (item['task_type'] == 'SLM'):
        duration = ((float(item['end']) - float(item['start'])) * 1000000)
        if (min > duration):
            min = duration

if (min < 300):
    time_scale = 5   # 1칸에 50us
else:
    time_scale = 100   # 1칸에 1ms

for item in items:
    start = ((float(item['start']) - start_time) * 1000000 / time_scale)
    duration = ((float(item['end']) - float(item['start'])) * 1000000 / time_scale)
    task = gantt.Task(name=item['task_name'], start=start, duration=duration, color=colors[int(item['task_id']) % len(colors)])

    for worker in worker_object:
        if worker['name'] == item['worker_name']:
            worker['object'].add_task(task)
            break

for po in worker_object:
    p.add_task(po['object'])

p.make_svg_for_tasks(filename='test_full.svg', start=0, end=int((end_time - start_time) / time_scale * 1000000), scale=time_scale*10)