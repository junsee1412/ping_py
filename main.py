import sys, time, random
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget
from gui.main_gui import Ui_MainWindow
from work.ping import ping

class Worker(QObject):

    sig_step = pyqtSignal(str, object)
    sig_done = pyqtSignal(str, object)
    sig_msg = pyqtSignal(str, object)

    def __init__(self, id: int, addr :str, count: int, ttl: int, size: int, timeout: float):
        super().__init__()
        self.__id = id
        self.__abort = False
        self.r = random.randint(0, 200)
        self.g = random.randint(0, 200)
        self.b = random.randint(0, 200)
        self.addr = addr
        self.count = count
        self.ttl = ttl
        self.size = size
        self.timeout = timeout
        self.per = [0,0]
        self.avr_time = []

    @pyqtSlot()
    def work(self):
        self.sig_msg.emit(f'PING {self.addr} data bytes', QColor(self.r, self.g, self.b))

        for step in range(1, self.count+1):
            self.per[0] += 1
            delay = ping(self.addr, seq=step, ttl=self.ttl, size=self.size, timeout=self.timeout)
            if delay is None:
                self.sig_step.emit(
                    f'{self.addr} timeout={self.timeout:.1f} s', QColor(self.r, self.g, self.b)
                    )
            elif delay is False:
                self.sig_step.emit(
                    f'{self.addr} Error', QColor(self.r, self.g, self.b)
                    )
            else:
                self.per[1] += 1
                self.avr_time.append(float(delay*1000))
                self.sig_step.emit(
                    f'{self.size} bytes from {self.addr}: icmp_seq={step} ttl={self.ttl} time={delay*1000:.1f} ms', QColor(self.r, self.g, self.b)
                    )

            app.processEvents()
            if self.__abort:
                self.sig_msg.emit(f'PING {self.addr} aborting work at icmp_seq {step}', QColor(self.r, self.g, self.b))
                break
            time.sleep(0.2)
        self.sig_msg.emit(self.data(), QColor(self.r, self.g, self.b))
        self.sig_done.emit(self.addr, QColor(self.r, self.g, self.b))

    def abort(self):
        self.sig_msg.emit(f'PING {self.addr} notified to abort', QColor(self.r, self.g, self.b))
        self.__abort = True
    
    def data(self):
        try:
            per = 100 - (self.per[1] *100 / self.per[0])
            min = self.avr_time[0]
            max = self.avr_time[-1]
            avg = sum(self.avr_time) / self.per[0]
            dat = f'PING {self.addr} {self.per[0]} packets transmitted, {self.per[1]} received, {per:.0f}% packet loss \nmin/avg/max {min:.3f}/{avg:.3f}/{max:.3f}'
            return dat
        except:
            return 'IP not found'


class PingGUI(QWidget):
    sig_abort_workers = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_win = QMainWindow()
        self.mwg = Ui_MainWindow()
        self.mwg.setupUi(self.main_win)

        self.mwg.btn_new.clicked.connect(self.new_host)
        self.mwg.btn_start.clicked.connect(self.start_threads)
        self.mwg.btn_stop.clicked.connect(self.abort_workers)
        self.mwg.btn_clear_log.clicked.connect(self.mwg.proc_log.clear)
        self.mwg.btn_clear_list.clicked.connect(self.clear_host)
        self.mwg.btn_remove.clicked.connect(self.remove_host)
        self.mwg.proc_list.clicked.connect(self.select_host)

        QThread.currentThread().setObjectName('main')
        self.__workers_done = None
        self.__threads = None
        self.__hosts = {}
        self.enable_start()

    
    def enable_start(self):
        if self.__hosts == {}:
            self.mwg.btn_start.setDisabled(True)
            self.mwg.btn_stop.setDisabled(True)
            self.mwg.btn_remove.setDisabled(True)
            self.mwg.btn_clear_list.setDisabled(True)
        else:
            self.mwg.btn_start.setEnabled(True)
            self.mwg.btn_clear_list.setEnabled(True)

    def clear_host(self):
        self.__hosts.clear()
        self.update_hosts()

    def remove_host(self):
        try:
            self.__hosts.pop(self.host_name)
        except:
            pass
        self.mwg.btn_remove.setDisabled(True)
        self.update_hosts()

    def select_host(self):
        self.item = self.mwg.proc_list.currentItem()
        self.host_name = self.item.text()
        self.mwg.btn_remove.setEnabled(True)
        self.mwg.line_ip.setText(self.host_name)
        host_attr = self.__hosts[self.host_name]
        self.setValue_to_gui(self.host_name, host_attr[0], host_attr[1], host_attr[3], host_attr[2])
        print(f'{self.host_name}: {self.__hosts[self.host_name]}')

    def new_host(self):
        new_host = self.getValue_from_gui()
        if new_host[0] != '':
            self.__hosts.update({new_host[0]: [new_host[1], new_host[2], new_host[3], new_host[4]],})
            self.update_hosts()
        self.setValue_to_gui('', 5, 64, 2, 56)

    def update_hosts(self):
        self.hosts = list(self.__hosts.keys())
        proc_list = self.mwg.proc_list
        proc_list.clear()
        for host in self.hosts:
            proc_list.addItem(host)
        self.enable_start()

    def start_threads(self):
        self.num = int(self.hosts.__len__())
        self.mwg.btn_start.setDisabled(True)
        self.mwg.btn_stop.setEnabled(True)

        self.__workers_done = 0
        self.__threads = []
        for idx in range(self.num):
            key = self.hosts[idx]
            attr = self.__hosts[key]
            worker = Worker(idx, key, attr[0], attr[1], attr[2], attr[3])
            thread = QThread()
            thread.setObjectName('thread_' + str(idx))
            self.__threads.append((thread, worker))
            worker.moveToThread(thread)

            worker.sig_step.connect(self.on_worker_step)
            worker.sig_done.connect(self.on_worker_done)
            worker.sig_msg.connect(self.msg_workers)

            self.sig_abort_workers.connect(worker.abort)

            thread.started.connect(worker.work)
            thread.start()

    def setValue_to_gui(self, addr:str, count: int, ttl: int, timeout: float, size: int):
        self.mwg.line_ip.setText(addr)
        self.mwg.spin_count.setValue(count)
        self.mwg.spin_ttl.setValue(ttl)
        self.mwg.spin_size.setValue(size)
        self.mwg.spin_timeout.setValue(timeout)

    def getValue_from_gui(self):
        host = self.mwg.line_ip.text().strip()
        count = int(self.mwg.spin_count.text())
        ttl = int(self.mwg.spin_ttl.text())
        size = int(self.mwg.spin_size.text())
        timeout = float(self.mwg.spin_timeout.text())
        return [host, count, ttl, size, timeout]

    @pyqtSlot(str, object)
    def msg_workers(self, msg: str, color):
        self.mwg.proc_log.setTextColor(color)
        self.mwg.proc_log.append(msg)

    @pyqtSlot(str, object)
    def on_worker_step(self, data: str, color):
        self.mwg.proc_log.setTextColor(color)
        self.mwg.proc_log.append(data)

    @pyqtSlot(str, object)
    def on_worker_done(self, addr: str, color):
        self.mwg.proc_log.setTextColor(color)
        self.mwg.proc_log.append(f'PING to {addr} done')
        self.__workers_done += 1
        if self.__workers_done == self.num:
            self.mwg.btn_start.setEnabled(True)
            self.mwg.btn_stop.setDisabled(True)

            for thread, worker in self.__threads:
                thread.quit()
                thread.wait()

    @pyqtSlot()
    def abort_workers(self):
        self.sig_abort_workers.emit()
        for thread, worker in self.__threads:
            thread.quit()
            thread.wait()

    def show(self):
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication([])

    form = PingGUI()
    form.show()

    sys.exit(app.exec_())