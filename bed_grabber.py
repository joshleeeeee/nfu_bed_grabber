import requests
import time
import threading
import argparse
import logging

def request_bed(ldid, room, ch):
    url = 'http://xsm.nfu.edu.cn/welcome/selectroom/selectbed?ldid={}&room={}&ch={}'.format(ldid, room, ch)
    headers = {
        'Cookie': 'JSESSIONID=YOUR_COOKIE_VALUE'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return None

def grab_bed(ldid, room, ch):
    res = request_bed(ldid, room, ch)
    if res is not None:
        msg = res['resultObject']
        logging.info(msg)
        if "不开放" in msg:
            return False
        return True
    else:
        return False

def main():
    parser = argparse.ArgumentParser(description='Bed Grabber')
    parser.add_argument('--ldid', required=True, help='楼栋号')
    parser.add_argument('--room', required=True, help='宿舍号')
    parser.add_argument('--ch', required=True, help='床号')
    parser.add_argument('--target-time', required=True, help='抢床位的时间，格式：YYYY-MM-DD HH:MM:SS')
    args = parser.parse_args()

    # 设置日志记录
    logging.basicConfig(filename='bed_grabber.log', encoding='utf-8',level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    # 设置抢床位的时间
    target_time = time.strptime(args.target_time, '%Y-%m-%d %H:%M:%S')
    logging.info(f"Target time: {args.target_time}")

    while True:
        current_time = time.localtime()
        logging.info(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S', current_time)}")
        if current_time >= target_time:
            # 当时间达到目标时间时，发送并发请求抢床位
            threads = []
            for _ in range(10):  # 可根据需求调整并发请求数量
                t = threading.Thread(target=grab_bed, args=(args.ldid, args.room, args.ch))
                threads.append(t)
                t.start()

            # 等待所有线程完成
            for t in threads:
                t.join()

            break
        else:
            # 未达到目标时间，等待一段时间后再检查时间
            time.sleep(0.5)

if __name__ == '__main__':
    main()
