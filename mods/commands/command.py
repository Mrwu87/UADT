import subprocess
from datetime import datetime, timedelta
from time import sleep
from mods.logs.log import service_logger


class Command():
    def run_command(self, command, taskId, cwd=None, timeout=600):
        try:
            service_logger.info('[COMMAND] [%s] RUN CMD: [%s], CWD: [%s], TIMEOUT: [%s]' %
                        (taskId, command, cwd, timeout))
            popen = subprocess.Popen(
                command,
                cwd=cwd,
                close_fds=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10000,
                shell=True
            )
            end_time = datetime.now() + timedelta(seconds=timeout)
            while True:
                stdout, stderr = popen.communicate()
                stdout_text = (stdout.decode('utf8')).strip()
                stderr_text = stderr.decode('utf8')
                try:
                    service_logger.info(stdout_text)
                except Exception as e:
                    pass

                if popen.poll() is not None:
                    break

                sleep(0.1)
                if end_time <= datetime.now():
                    popen.kill()
                    service_logger.critical('[COMMAND] [%s] EXEC TIMEOUT' % (taskId))
                    return False, None, None

            if popen.returncode > 0:
                service_logger.info('[COMMAND] [%s] FAILED:[%s], CODE:[%s], \nSTDOUT:[\n%s\n]\nSTDERR:[\n%s\n]' % (
                    taskId, command, popen.returncode, stdout_text, stderr_text))

                return False
            else:
                service_logger.info('[COMMAND] [%s] SUCCESS:[%s], CODE:[%s]' %
                            (taskId, command, popen.returncode))
                return True
        except Exception as e:
            service_logger.exception('[COMMAND] [%s] EXCEPTION:[%s]:' % (taskId, command))
            return False

