function getTimeSpanString(start, end)
{
    if (end < start)
        end = start;

    var t_left = (end - start) / 1000;

    var seconds = Math.floor(t_left % 60);
    t_left = t_left / 60;
    var minutes = Math.floor(t_left % 60);
    t_left = t_left / 60;
    var hours = Math.floor(t_left % 24);
    t_left = t_left / 24;
    var days = Math.floor(t_left);
    return "" + days + " days, " + hours + ":" + minutes + ":" + seconds;
}