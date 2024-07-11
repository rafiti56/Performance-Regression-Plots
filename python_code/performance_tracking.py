

time = 20
timers = {"Architecture": {"Timer": []}}

i = 0
prev_date = 0

list_dates = []

for key, value in timers.items():
    for kay, val in value.items():
    
        date = value[i]
        if date > prev_date:
            i += 1
            prev_date = date

            list_dates.append(date[i])

#can use pyqt6 for dashboard

