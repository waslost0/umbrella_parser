import datetime


timing_list = []
with open("times_data.txt", "r") as file:
    timing_list = file.read()


timing_list = timing_list.split('\n')


def get_curr_time():
    curr_time = datetime.datetime.now().strftime("%H:%M")
    curr_time_list = list(curr_time)
    curr_time_list[-1] = str(int(curr_time_list[-1]) + 1)
    return ''.join(curr_time_list)


while True:
    curr_time = ''
    curr_time = get_curr_time()
    print(curr_time)
    if curr_time in timing_list:
        print(curr_time)
        print('Time to solve captcha')
        print(datetime.datetime.now().strftime("%H:%M"))
        break
