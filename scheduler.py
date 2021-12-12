#! /usr/bin/env python3

# Add arrival time and STCF

from __future__ import print_function
import sys
from optparse import OptionParser
import random

# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system", action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times", action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job", action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: SJF, FIFO, RR", action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")
# 아래에 추가
parser.add_option("-a", "--time", default="", help="set arrival time for each job", action="store", type="string", dest="time")

(options, args) = parser.parse_args()

random_seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
    print('ARG jobs', options.jobs)
    print('ARG maxlen', options.maxlen)
    print('ARG seed', options.seed)
else:
    print('ARG jlist', options.jlist)
print('')

print('Here is the job list, with the run time of each job: ')

import operator

joblist = []

# 옵션으로 받은 arrival time을 배열로 생성
if options.time != "":
    arrivaltime = []
    for time in options.time.split(','):
        arrivaltime.append(float(time))

if options.jlist == '':
    if options.time == "":  #옵션으로 arrival time을 받지 않았을 때: 이전과 동일하게 동작
        for jobnum in range(0,options.jobs):
            runtime = int(options.maxlen * random.random()) + 1
            joblist.append([jobnum, runtime])
            print('  Job', jobnum, '( length = ' + str(runtime) + ' )')
    else:  #아래 추가: 옵션으로 arrival time을 받았을 때: joblist에 arrival time도 함께 저장
        for jobnum in range(0,options.jobs):
            runtime = int(options.maxlen * random.random()) + 1
            joblist.append([jobnum, runtime, arrivaltime[jobnum]])

        joblist = sorted(joblist, key=operator.itemgetter(2))

        for i in range(0,len(joblist)):
            joblist[i][0] = i
            print('  Job', i, '( length = ' + str(joblist[i][1]) + ', arrival time = ' + str(joblist[i][2]) + ' )')
else:
    jobnum = 0
    if options.time == "":  #옵션으로 arrival time을 받지 않았을 때: 이전과 동일하게 동작
        for runtime in options.jlist.split(','):
            joblist.append([jobnum, float(runtime)])
            jobnum += 1
        for job in joblist:
            print('  Job', job[0], '( length = ' + str(job[1]) + ' )')
    else:  #아래 추가: 옵션으로 arrival time을 받았을 때: joblist에 arrival time도 함께 저장
        for runtime in options.jlist.split(','):
            joblist.append([jobnum, float(runtime), arrivaltime[jobnum]])
            jobnum += 1

        joblist = sorted(joblist, key=operator.itemgetter(2))

        for i in range(0,len(joblist)):
            joblist[i][0] = i
            print('  Job', i, '( length = ' + str(joblist[i][1]) + ', arrival time = ' + str(joblist[i][2]) + ' )')

print('\n')

if options.solve == True:
    print('** Solutions **\n')

    #아래에 추가: STCF 새로 작성
    if options.policy == "STCF":
        if options.time == "":
            options.policy == "SJF"
        else:
            joblist = sorted(joblist, key=operator.itemgetter(2,1))
            jobcount = len(joblist)
            response = []
            turnaround = []
            for o in range(0,jobcount):
                response.append(None)
                turnaround.append(None)
            wait = []
            thetime = joblist[0][2]  #프로세스가 돌아가기 시작한 시간
            tasklist = joblist
            queue = []  #밀린 프로세스
            contextSwitch = 0
            i = 0
            tmp = 0
            sjf = 0

            while jobcount > 0:
                while 1:
                    if sjf == 1:
                        for i in range(0, len(tasklist)):
                            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                            if response[tasklist[i][0]] == None:
                                response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                            turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                            thetime = thetime + tasklist[i][1]
                            jobcount -= 1
                        break
                    if len(tasklist) == 1:
                        print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                        if response[tasklist[i][0]] == None:
                            response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                        turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                        jobcount -= 1
                        break
                    checkAll = 1
                    for j in range(i + 2,jobcount):
                        if thetime + tasklist[i][1] > tasklist[j][2] and thetime == tasklist[i + 1][2]:
                            checkAll = 0
                            contextSwitch = j
                            break
                    check = (thetime == tasklist[i + 1][2] and checkAll) or ((thetime + tasklist[i][1]) < tasklist[i + 1][2])
                    if check:  #실행 도중 다른 job이 arrival하지 않았을 때
                        print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                        if response[tasklist[i][0]] == None:
                            response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                        turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                        jobcount -= 1
                        if thetime == tasklist[i + 1][2]:  #동시에 도착한 job이 있을 때
                            thetime = thetime + tasklist[i][1]
                            i += 1
                            break
                        elif queue == []:  #대기 중인 job이 없을 때
                            thetime = tasklist[i + 1][2]
                            i += 1
                            break
                        else:  #대기 중인 job이 있을 때
                            thetime = thetime + tasklist[i][1]
                            index = queue[0][0]
                            if tasklist[i + 1][2] - thetime < tasklist[index][1]:  #대기 중인 첫 번째 job의 남은 실행 시간이 빈 시간보다 클 때
                                tasklist[index][1] = tasklist[index][1] - (tasklist[i + 1][2] - thetime)
                                if tasklist[index][1] <= tasklist[i + 1][1]:  #실행 중인 job의 남은 실행 시간이 다음 job의 실행 시간 보다 작거나 같을 때
                                    queue.append(tasklist[i + 1])
                                    tasklistN = tasklist
                                    tasklist = []
                                    tasklist.append(tasklistN[index])
                                    for m in range(2, jobcount - i):
                                        tasklist.append(tasklistN[i + m])
                                    i = 0
                                    queue.pop(0)
                                    break
                                else:
                                    print('  [ time %3d ] Run job %d for %.2f secs ( %.2f left )' % (thetime, tasklist[index][0], tasklist[i + 1][2] - thetime, tasklist[index][1]))
                                    if response[tasklist[index][0]] == None:
                                        response[tasklist[index][0]] = [tasklist[index][0], thetime - tasklist[index][2]]
                                    i += 1
                                    thetime = tasklist[i][2]
                                    break
                            elif tasklist[i + 1][2] - thetime == tasklist[index][1]: #대기 중인 첫 번째 job의 남은 실행 시간이 빈 시간과 같을 때
                                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[index][0], tasklist[index][1], thetime + tasklist[index][1]))
                                if response[tasklist[index][0]] == None:
                                    response[tasklist[index][0]] = [tasklist[index][0], thetime - tasklist[index][2]]
                                turnaround[tasklist[index][0]] = [tasklist[index][0], thetime + tasklist[index][1] - tasklist[index][2]]
                                jobcount -= 1
                                i += 1
                                thetime = tasklist[i][2]
                                queue.pop(0)  #대기열에서 제거
                                break
                            else:  #대기 중인 첫 번째 job의 남은 실행 시간이 빈 시간보다 작을 때
                                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[index][0], tasklist[index][1], thetime + tasklist[index][1]))
                                if response[tasklist[index][0]] == None:
                                    response[tasklist[index][0]] = [tasklist[index][0], thetime - tasklist[index][2]]
                                turnaround[tasklist[index][0]] = [tasklist[index][0], thetime + tasklist[index][1] - tasklist[index][2]]
                                jobcount -= 1
                                thetime = thetime + tasklist[index][1]
                                queue.pop(0)  #대기열에서 제거
                                #두 번째 대기 중인 job 실행
                                index = queue[0][0]
                                tasklist[index][1] = tasklist[index][1] - (tasklist[i + 1][2] - thetime)
                                if tasklist[index][1] <= tasklist[i + 1][1]:  #실행 중인 job의 남은 실행 시간이 다음 job의 실행 시간 보다 작거나 같을 때
                                    queue.append(tasklist[i + 1])
                                    tasklistN = tasklist
                                    tasklist = []
                                    tasklist.append(tasklistN[index])
                                    for m in range(2, jobcount - i):
                                        tasklist.append(tasklistN[i + m])
                                    i = 0
                                    queue.pop(0)
                                    break
                                else:
                                    print('  [ time %3d ] Run job %d for %.2f secs ( %.2f left )' % (thetime, tasklist[index][0], tasklist[i + 1][2] - thetime, tasklist[index][1]))
                                    if response[tasklist[index][0]] == None:
                                        response[tasklist[index][0]] = [tasklist[index][0], thetime - tasklist[index][2]]
                                    i += 1
                                    thetime = tasklist[i][2]
                                    break
                    elif checkAll == 0 and contextSwitch != 0:  #실행 중인 job의 다음 job 이후에 충돌이 있을 때
                        tasklist[i][1] = tasklist[i][1] - (tasklist[contextSwitch][2] - thetime)
                        if tasklist[i][1] <= tasklist[contextSwitch][1]:  #실행 중인 job의 남은 실행 시간이 더 적을 때
                            for k in range(i + 1, contextSwitch + 1):
                                queue.append(tasklist[k])
                            tasklistN = tasklist
                            tasklist =[]
                            tasklist.append(tasklistN[i])
                            for n in range(contextSwitch + 1, jobcount):
                                tasklist.append(tasklistN[n])
                            i = 0
                            break
                        else:
                            print('  [ time %3d ] Run job %d for %.2f secs ( %.2f left )' % (thetime, tasklist[i][0], tasklist[contextSwitch][2] - thetime, tasklist[i][1]))
                            if response[tasklist[i][0]] == None:
                                    response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                            thetime = tasklist[contextSwitch][2]
                            for k in range(i, contextSwitch):
                                queue.append(tasklist[k])
                            i = contextSwitch
                            break
                    else:  #실행 도중 다른 job이 arrival했을 때
                        leftTime = tasklist[i][1] - (tasklist[i + 1][2] - thetime)
                        leftTimeCheck = (leftTime <= tasklist[i + 1][1])
                        if leftTimeCheck:  #진행 중인 프로세스의 시간이 다음 프로세스의 runtime보다 더 적게 남았을 때
                            # queue.append(tasklist[i + 1])
                            if i + 2 <= len(tasklist) - 1 and (thetime + tasklist[i][1]) < tasklist[i + 2][2]:  #다음 다음 프로세스의 도착 시간이 현재 진행 중인 프로세스가 끝난 후 일 때
                                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                                if response[tasklist[i][0]] == None:
                                    response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                                turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                                thetime = thetime + tasklist[i][1]
                                i += 1
                                jobcount -= 1
                                break
                            elif i + 2 <= len(tasklist) - 1 and (thetime + tasklist[i][1]) == tasklist[i + 2][2]:
                                queue.append(tasklist[i + 1])
                                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                                if response[tasklist[i][0]] == None:
                                    response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                                turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                                thetime = thetime + tasklist[i][1]
                                i = i + 2
                                jobcount -= 1
                                break
                            elif i + 2 <= len(tasklist) - 1:  #다음 다음 프로세스의 도착 시간이 현재 진행 중인 프로세스가 끝나기 전인 경우
                                queue.append(tasklist[i + 1])
                                leftTime = tasklist[i][1] - (tasklist[i + 2][2] - thetime)
                                leftTimeCheck = leftTime < tasklist[i + 2][1]
                                if leftTimeCheck:  #진행 중인 프로세스의 남은 시간이 다음 다음 프로세스의 남은 시간보다 적을 때
                                    queue.append(tasklist[i + 2])
                                    tasklistN = tasklist
                                    tasklist = []
                                    tasklist.append(tasklist[i])
                                    for l in range (i + 3, jobcount):
                                        tasklist.append(tasklist[l])
                                    i = o
                                    break
                                else:
                                    tasklist[i][1] = tasklist[i][1] - (tasklist[i + 2][2] - thetime)
                                    print('  [ time %3d ] Run job %d for %.2f secs ( %.2f left )' % (thetime, tasklist[i][0], tasklist[i + 2][2] - thetime, tasklist[i][1]))
                                    if response[tasklist[i][0]] == None:
                                        response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                                    queue.append(tasklist[i])
                                    i = i + 2
                                    thetime = tasklist[i][2]
                                    break
                            else:  #다음 다음 프로세스가 없을 때
                                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, tasklist[i][0], tasklist[i][1], thetime + tasklist[i][1]))
                                if response[tasklist[i][0]] == None:
                                    response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                                turnaround[tasklist[i][0]] = [tasklist[i][0], thetime + tasklist[i][1] - tasklist[i][2]]
                                thetime = thetime + tasklist[i][1]
                                i += 1
                                jobcount -= 1
                                break
                        else:  #진행 중인 프로세스의 시간이 다음 프로세스의 runtime보다 많을 때
                            tasklist[i][1] = tasklist[i][1] - (tasklist[i + 1][2] - thetime)
                            print('  [ time %3d ] Run job %d for %.2f secs ( %.2f left )' % (thetime, tasklist[i][0], tasklist[i + 1][2] - thetime, tasklist[i][1]))
                            if response[tasklist[i][0]] == None:
                                    response[tasklist[i][0]] = [tasklist[i][0], thetime - tasklist[i][2]]
                            queue.append(tasklist[i])
                            i += 1
                            thetime = tasklist[i][2]
                            break
                if i >= len(tasklist) - 1:  #out of range 방지
                    tasklistN = tasklist
                    tasklist = []
                    tasklist.append(tasklistN[i])
                    for p in range(0, len(queue)):
                        if tasklist[0] != queue[p]:
                            tasklist.append(queue[p])
                    i = 0
                    sjf = 1

            print('\nFinal statistics:')
            count = len(joblist)
            responseSum = 0
            turnaroundSum = 0
            for q in range(0, count):
                print('  Job %3d -- Response: %3.2f  Turnaround %3.2f' % (response[q][0], response[q][1], turnaround[q][1]))
                responseSum += response[q][1]
                turnaroundSum += turnaround[q][1]
            print('\n  Average -- Response: %3.2f  Turnaround %3.2f\n' % (responseSum/count, turnaroundSum/count))

    if options.policy == 'SJF':
        if options.time == "":  #옵션으로 arrival time을 받지 않았을 때: 이전과 동일하게 동작
            joblist = sorted(joblist, key=operator.itemgetter(1))
            options.policy = 'FIFO'
        else:  #아래 추가: 옵션으로 arrival time을 받았을 때: 다중 수준의 정렬로 arrival time 순으로 정렬하고 그 다음 runtime이 짧은 순으로 정렬
            joblist = sorted(joblist, key=operator.itemgetter(2,1))
            options.policy = 'FIFO'

    if options.policy == 'FIFO':
        if options.time == "":  #옵션으로 arrival time을 받지 않았을 때: 이전과 동일하게 동작
            thetime = 0
            print('Execution trace:')
            for job in joblist:
                print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
                thetime += job[1]

            print('\nFinal statistics:')
            t     = 0.0
            count = 0
            turnaroundSum = 0.0
            waitSum       = 0.0
            responseSum   = 0.0
            for tmp in joblist:
                jobnum  = tmp[0]
                runtime = tmp[1]
                
                response   = t
                turnaround = t + runtime
                wait       = t
                print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
                responseSum   += response
                turnaroundSum += turnaround
                waitSum       += wait
                t += runtime
                count = count + 1
            print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
        else:  #아래 추가: 옵션으로 arrival time을 받았을 때:
            joblist = sorted(joblist, key=operator.itemgetter(2))  #joblist를 arrival time 순으로 정렬
            thetime = joblist[0][2]  #첫 실행 시작 시간을 첫 job의 arrival time으로 설정
            #reponse, turnaround, wait 시간을 기록할 배열 설정 및 평균을 위한 count 초기값 설정
            response = []
            turnaround = []
            wait = []
            count = 0
            print('Execution trace:')
            for job in joblist:
                if thetime < job[2]:  #이전 job이 끝난 시점이 다음 job의 arrival time보다 일찍인 경우
                    thetime = job[2]  #시작 시점을 다음 job의 arrival time으로 한다
                    print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
                    thetime += job[1]
                    response.append([job[0], thetime-job[1]-job[2]])
                    turnaround.append([job[0], thetime-job[2]])
                    wait.append([job[0], thetime - job[1] - job[2]])
                    count += 1

                else:
                    print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
                    thetime += job[1]
                    response.append([job[0], thetime - job[1] - job[2]])
                    turnaround.append([job[0], thetime - job[2]])
                    wait.append([job[0], thetime - job[1] - job[2]])
                    count += 1

            print('\nFinal statistics:')
            turnaroundSum = 0.0
            waitSum       = 0.0
            responseSum   = 0.0
            #아래 추가: analysis 새로 정의 후 이를 통해 데이터 추출
            joblist = sorted(joblist, key=operator.itemgetter(0))
            response = sorted(response, key=operator.itemgetter(0))
            turnaround = sorted(turnaround, key=operator.itemgetter(0))
            wait = sorted(wait, key=operator.itemgetter(0))
            analysis = [joblist, response, turnaround, wait]
            for i in range(0, count):
                jobnum  = analysis[0][i][0]
                runtime = analysis[0][i][1]
                
                response   = analysis[1][i][1]
                turnaround = analysis[2][i][1]
                wait       = analysis[3][i][1]
                print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
                responseSum   += response
                turnaroundSum += turnaround
                waitSum       += wait
            print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        if options.time == "":  #옵션으로 arrival time을 받지 않았을 때: 이전과 동일하게 동작
            print('Execution trace:')
            turnaround = {}
            response = {}
            lastran = {}
            wait = {}
            quantum  = float(options.quantum)
            jobcount = len(joblist)
            for i in range(0,jobcount):
                lastran[i] = 0.0
                wait[i] = 0.0
                turnaround[i] = 0.0
                response[i] = -1

            runlist = []
            for e in joblist:
                runlist.append(e)

            thetime  = 0.0
            while jobcount > 0:
                job = runlist.pop(0)
                jobnum  = job[0]
                runtime = float(job[1])
                if response[jobnum] == -1:
                    response[jobnum] = thetime
                currwait = thetime - lastran[jobnum]
                wait[jobnum] += currwait
                if runtime > quantum:
                    runtime -= quantum
                    ranfor = quantum
                    print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                    runlist.append([jobnum, runtime])
                else:
                    ranfor = runtime;
                    print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                    turnaround[jobnum] = thetime + ranfor
                    jobcount -= 1
                thetime += ranfor
                lastran[jobnum] = thetime

            print('\nFinal statistics:')
            turnaroundSum = 0.0
            waitSum       = 0.0
            responseSum   = 0.0
            for i in range(0,len(joblist)):
                turnaroundSum += turnaround[i]
                responseSum += response[i]
                waitSum += wait[i]
                print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
            count = len(joblist)
            
            print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
        
        else:  #아래 추가: 옵션으로 arrival time을 받았을 때:
            print('Execution trace:')
            turnaround = {}
            response = {}
            lastran = {}
            wait = {}
            quantum  = float(options.quantum)

            runlist = []
            runlist.append(joblist[0])

            tasklist = []
            for e in joblist:
                tasklist.append(e)
            jobcount = len(tasklist)

            #정보 초기값 설정
            for i in range(0,jobcount):
                lastran[i] = joblist[i][2]
                wait[i] = 0.0
                turnaround[i] = 0.0
                response[i] = -1

            thetime = 0

            while jobcount > 0:
                job = runlist.pop(0)
                if job[2] != None and thetime < job[2]:
                    print("  [ time %3d ] CPU rest" % (thetime))
                    thetime = job[2]
                    runlist.append(job)
                else:
                    jobnum  = job[0]
                    runtime = float(job[1])
                    if response[jobnum] == -1:
                        response[jobnum] = thetime - job[2]
                        for j in range(0, len(tasklist)):
                            if tasklist[j][0] == jobnum:
                                tasklist[j] = [jobnum, runtime, None]
                    currwait = thetime - lastran[jobnum]
                    wait[jobnum] += currwait
                    if runtime > quantum:
                        runtime -= quantum
                        ranfor = quantum
                        print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                        for task in tasklist:
                            if task[0] != jobnum and task[2] != None and task[2] <= thetime + 10:
                                runlist.append(task)
                                for i in range(0, len(tasklist)):
                                    if tasklist[i][0] == task[0]:
                                        tasklist[i] = [task[0], task[1], None]
                        runlist.append([jobnum, runtime, None])
                    else:
                        ranfor = runtime;
                        print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                        turnaround[jobnum] = thetime + ranfor - joblist[jobnum][2]
                        for k in range(0, len(tasklist)):
                            if tasklist[k][0] == jobnum:
                                tasklist.pop(k)
                                break
                        jobcount -= 1
                        if runlist == [] and tasklist != []:
                            runlist.append(tasklist[0])
                    lastran[jobnum] = thetime
                    thetime += ranfor

            print('\nFinal statistics:')
            turnaroundSum = 0.0
            waitSum       = 0.0
            responseSum   = 0.0
            for i in range(0,len(joblist)):
                turnaroundSum += turnaround[i]
                responseSum += response[i]
                waitSum += wait[i]
                print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
            count = len(joblist)
            
            print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    #아래에 추가: and options.policy != 'STCF'
    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR' and options.policy != 'STCF': 
        print('Error: Policy', options.policy, 'is not available.')
        sys.exit(0)
else:
    print('Compute the turnaround time, response time, and wait time for each job.')
    print('When you are done, run this program again, with the same arguments,')
    print('but with -c, which will thus provide you with the answers. You can use')
    print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
    print('to generate different problems for yourself.')
    print('')
