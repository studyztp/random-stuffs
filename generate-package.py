from pathlib import Path
from distutils.dir_util import copy_tree

package_out_path = Path("//home/ubuntu/spec2006-package")
spec2006_source_path = Path("/home/ubuntu/spec2006/benchspec/CPU2006")
benchmarks = []

for bench in spec2006_source_path.iterdir():
    if bench.is_dir():
        name = (bench.name).split(".")[1]
        if name != "specrand":
            print(name)
            if Path(bench / "exe").exists():
                benchmarks.append(name)
                bench_package_path = Path(package_out_path / f"{name}")
                bench_package_path.mkdir(exist_ok=True)
                Path(bench_package_path / "exe").mkdir(exist_ok=True)
                copy_tree(
                    Path(bench / "exe").as_posix(),
                    Path(bench_package_path / "exe").as_posix(),
                )
                bench_package_input_path = Path(bench_package_path / "input")
                bench_package_input_path.mkdir(exist_ok=True)
                Path(bench_package_input_path / "ref").mkdir(exist_ok=True)
                Path(bench_package_input_path / "train").mkdir(exist_ok=True)
                if Path(bench / "data/all").exists():
                    for inputs in Path(bench / "data/all").iterdir():
                        copy_tree(
                            inputs.as_posix(),
                            Path(bench_package_input_path / "ref").as_posix(),
                        )
                        copy_tree(
                            inputs.as_posix(),
                            Path(bench_package_input_path / "train").as_posix(),
                        )
                for inputs in Path(bench / "data/ref").iterdir():
                    if inputs.name == "input":
                        copy_tree(
                            inputs.as_posix(),
                            Path(bench_package_input_path / "ref").as_posix(),
                        )
                for inputs in Path(bench / "data/train").iterdir():
                    if inputs.name == "input":
                        copy_tree(
                            inputs.as_posix(),
                            Path(bench_package_input_path / "train").as_posix(),
                        )

print(benchmarks)
