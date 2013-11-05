
def orgmode_write(tasks):
    """
    Writes a list of Task objects into a String in Org-Mode format
    """
    s = []
    # header
    s.append('#+PRIORITIES: A B B')
    s.append('\n\n')
    # contents 
    for task in tasks:
        # start
        s.append('* ')
        # completion
        if task.is_completed:
            s.append('DONE ')
        else:
            s.append('TODO ')
        # priority
        if task.priority == 'HIG':
            s.append('[#A] ')
        else:
            s.append('[#B] ')
        # task
        s.append(task.task)
        # end
        s.append('\n')

        # finished date
        if task.is_completed:
            s.append('  CLOSED: [%s]' % 
                     task.date_completed.strftime("%Y-%m-%d %a %H:%M"))
            s.append('\n')

    return "".join(s)
