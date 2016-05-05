import threading,  multiprocessing
import queue

NUM_THREADS = 10

def min(a,b):
    if a < b:
        return a
    return b

def threaded_map(fn,worklist,args=[],num_t=NUM_THREADS):
    # note that this threaded map makes no guarantees about the order in which it will return anything
    ret = []
    q = queue.Queue()

    def worker():
        while not q.empty():
            w = q.get()
            result = fn(w,*args)
            ret.append(result)
            q.task_done()

    for i in worklist:
        q.put(i)

    for i in range(min(num_t, len(worklist))):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        
    #print(worklist)
    q.join()
    return ret


# the following function applies each of the functions in fnlist
# and returns the function that achieved the max length
def apply_max(obj,fnlist):
    max = -1
    for fn in fnlist:
        tmp_result = fn(obj)
        tmp_count = len(tmp_result)
        if(tmp_count > max):
            retfn = fn
            max = tmp_count
            result = tmp_result
    return (result, retfn)

def ret_max(obj,fnlist):
    max = -1
    for fn in fnlist:
        tmp_result = fn(obj)
        tmp_count = len(tmp_result)
        if(tmp_count > max):
            retfn = fn
            max = tmp_count
            #result = tmp_result
    return retfn


def do_every (interval, worker_func, args, iterations = 0):
    if iterations != 1:
        threading.Timer (
            interval,
            do_every,
            [interval, worker_func, args, 0 if iterations == 0 else iterations-1]
        ).start ()
        
        worker_func(*args)

        
def flatten(listOfLists):
    return [item for sublist in listOfLists for item in sublist]
