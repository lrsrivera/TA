from task_manager.singletons.logger_singleton import LoggerSingleton


logger1 = LoggerSingleton().get_logger()
logger2 = LoggerSingleton().get_logger()


assert logger1 is logger2, "Logger Singleton failed! Instances are different."


logger1.info("Logger Singleton is working!")

print("Logger test completed successfully!")
