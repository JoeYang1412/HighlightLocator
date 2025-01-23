class time_format:
    """
    Convert time format between seconds and hours, minutes, and seconds.
    methods:
        sec_to_time(sec): Convert seconds to hours, minutes, and seconds.
        time_to_sec(hour, minute, second): Convert hours, minutes, and seconds to seconds.
    """
    def sec_to_time(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)
    def time_to_sec(hour, minute, second):
        return int(hour) * 3600 + int(minute) * 60 + int(second)
        
    

