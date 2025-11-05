from datetime import datetime
from functools import wraps
import json
import os
import shutil
import jsonlines
import pandas as pd
import tqdm


class TestInstance:
    def __init__(self,
                 from_dir="./",
                 to_dir="./result/",
                 suffix=".jsonl",
                 time_type=-1,
                 max_iter=None,
                 log=1,
                 step=None,
                 just_test=0):
        '''
            from_dir, The original folder where the test question was
            to_dir, Folder for storing results
            suffix, Filter files by suffix
            time_type=-1, 
            max_iter=0
        '''
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.suffix = suffix if "." in suffix else "." + suffix
        self.error_dir = os.path.join(to_dir, "errors")
        self.log_file = os.path.join(to_dir, "logs")
        self.now_str = self.generate_now_str(time_type=time_type)
        self.just_test = just_test
        self.step = step

    def generate_now_str(self, time_type=1):
        now = datetime.now()
        now_str = ""
        if time_type < 0:
            return ""
        if time_type:
            now_str = str(int(datetime.timestamp(now)))
        else:
            now_str = now.strftime("%Y%m%d/%H%M%S")
        return now_str

    def run_dict(self, dict_data):
        return dict_data

    def check_dir(self, file_or_folder):
        target_dir = os.path.dirname(file_or_folder)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    def log(self, info):
        log_dir = os.path.dirname(self.log_file)
        self.check_dir(log_dir)
        with open(self.log_file, "a") as file:
            file.write("\n" + info)

    def run_and_save_jsonlines(self, func, *args, **kwargs):
        with jsonlines.open(self.source_file) as reader:
            items = 0
            with jsonlines.open(self.target_file, mode='w') as writer:
                for instance in tqdm(reader):
                    items += 1
                    if items > self.max_iter:
                        break
                    try:
                        result_data = func(instance, *args, **kwargs)
                        if result_data:
                            writer.write(result_data)
                    except Exception as e:
                        self.log(
                            f"run_and_save_jsonlines:\n{e.__class__.__name__} : {str(e)}, items : {items}")

    def run_chunk(self, instance):
        loop = True
        if isinstance(instance, pd.core.frame.DataFrame):
            for x in range(0, instance.shape[0], self.step):
                yield instance[x:x+self.step]
        else:
            while loop:
                try:
                    yield instance.get_chunk(self.step)
                except StopIteration:
                    loop = False

    def run_and_save_table(self, func, *args, **kwargs):
        if self.step:
            if ".xlsx" == self.suffix or ".xls" == self.suffix:
                instance = pd.read_excel(self.source_file)
            elif ".csv" == self.suffix:
                instance = pd.read_csv(self.source_file, iterator=True)
            for i, par_data in enumerate(self.run_chunk(instance)):
                target_file = self.target_file.replace(
                        self.suffix, f"_{i}{self.suffix}")
                if os.path.exists(target_file):
                    continue
                result_data = func(par_data, *args, **kwargs)
                result_data.to_excel(target_file, index=False)
        else:
            if ".xlsx" == self.suffix or ".xls" == self.suffix:
                instance = pd.read_excel(self.source_file)
            elif ".csv" == self.suffix:
                instance = pd.read_csv(self.source_file)
            result_data = func(instance, *args, **kwargs)
            result_data.to_csv(self.target_file, index=False)

    def run_and_save_default(self, func, *args, **kwargs):
        with open(self.source_file, "r") as f:
            instance = f.read()
        with open(self.target_file, mode='w') as writer:
            try:
                result_data = func(instance, *args, **kwargs)
                if result_data:
                    writer.write(result_data)
            except Exception as e:
                self.log(
                    f"run_and_save_default:\n{e.__class__.__name__} : {str(e)}")

    def run_and_save(self, func, *args, **kwargs):
        if ".jsonl" == self.suffix:
            self.run_and_save_jsonlines(func, *args, **kwargs)
        elif self.suffix in [".csv", ".xlsx", ".xls"]:
            self.run_and_save_table(func, *args, **kwargs)
        else:
            self.run_and_save_default(func, *args, **kwargs)

    def run_func(self, from_dir, to_dir, func, *args, **kwargs):
        for root, dirs, files in os.walk(from_dir):
            # print(from_dir, root, dirs, files)
            for f in files:
                self.source_file = os.path.join(root, f)
                self.target_file = os.path.join(
                    root.replace(from_dir, to_dir), f)
                print(self.target_file)
                if os.path.exists(self.target_file):
                    continue
                self.check_dir(self.target_file)
                if self.suffix in self.source_file:
                    try:
                        self.run_and_save(func, *args, **kwargs)
                    except Exception as e:
                        self.log(
                            f"run file error {self.source_file}\n{e.__class__.__name__} : {str(e)}")
                        self.error_file = os.path.join(
                            root.replace(from_dir, self.error_dir), f)
                        self.check_dir(self.error_file)
                        shutil.copyfile(self.source_file, self.error_file)
                if self.just_test:
                    break
            if self.just_test:
                break

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(self.from_dir, str):
                self.run_func(self.from_dir, self.to_dir,
                              func, *args, **kwargs)
            elif isinstance(self.from_dir, list):
                for from_dir in self.from_dir:
                    to_dir = os.path.join(
                        self.to_dir, from_dir.split(os.sep)[-1])
                    self.run_func(from_dir, to_dir, func, *args, **kwargs)
        return wrapper
