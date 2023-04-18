## How to restore a SPEC2006 checkpoint

### Configuration Script

In order to restore a checkpoint, it requires the checkpoint, the index of the checkpoint, the executable, and the path to the SimPoint files.

Example:

``` Python

board = RISCVMatchedBoard(
    clk_freq="1.2GHz",
    l2_size="2MB",
    is_fs=False,
)

simpoint = SimpointDirectoryResource(

    local_path=# path to the SimPoint files,

    # The `simpoint_file` takes in the name of the simulation point file. The SimPoint 3.2 defaults the output simulation point file name as "results.simpts".
    simpoint_file="results.simpts",

    # Same as above, the `weight_file` takes in the name of the weight file. The SimPoint 3.2 defaults it as "results.weights".
    weight_file="results.weights",

    # The below information depends on how the checkpoint was taken
    warmup_interval=200000000,
    simpoint_interval=100000000
)

board.set_se_binary_workload(
    binary=CustomResource(
        # path to the executable/binary
    )
)

# This function is an example of an exit event for restoring a SimPoint checkpoint.
# It dumps and resets stats after reaching the end of the warmup interval. After reaching the end of the simulation interval, it exits the simulation loop.
def max_inst():
    warmed_up = False
    while True:
        if warmed_up:
            print("end of SimPoint interval")
            yield True
        else:
            print("end of warmup, starting to simulate SimPoint")
            warmed_up = True
            # Schedule a MAX_INSTS exit event during the simulation
            simulator.schedule_max_insts(simpoint.get_simpoint_interval())
            print(f"simpoint interval: {simpoint.get_simpoint_interval()}")
            dump()
            reset()
            yield False

simulator = Simulator(
    board=board,

    # For example:
    # checkpoint_path="/projects/gem5/riscv-spec2006/checkpoints/data/train/astar/0/se_checkpoint_dir/cpt.SimPoint0"
    # Inside the "cpt.SimPoint0", there should be a "board.physmem.store0.pmem" and a "m5.cpt" file. 
    checkpoint_path= # path to the checkpoint
    
    # Setup the exit events
    on_exit_event={ExitEvent.MAX_INSTS: max_inst()},
)

# This part if to check if the warmup length for this checkpoint equals to zero, if so, it should set the `schedule_max_insts` to stop at 1 inst because `schedule_max_insts` doesn't schedule any events when the input is 0.
if(simpoint.get_warmup_list()[
    # the index of the checkpoint
    # for example, for "cpt.SimPoint0", the index should be 0.
] == 0):
    simulator.schedule_max_insts(1)
else:
    simulator.schedule_max_insts(simpoint.get_warmup_list()[
        #  the index of the checkpoint
    ])

simulator.run()

```

### Bash script example

Because each benchmark in SPEC2006 might have more than one execution with different inputs, and each execution usually have more than one checkpoint, it would be helpful to have a bash script to restore checkpoints in a unit of the benchmark.

Based on the structure of how the checkpoints are stored, I found this bash script might be helpful:

``` sh
# the path to gem5.opt
gem5optDir=$1

# the name of the benchmark, e.x. mcf
bench=$2

# the size of the input, e.x. input
size=$3

# create a restore directory
mkdir restore-$bench-$size
cd restore-$bench-$size

# execution index
index=0

# initialize paths
# path to the checkpoint workplace
benchDir=/projects/gem5/riscv-spec2006/checkpoints/data/$size/$bench/$index
# path to the executable
benchExe=$benchDir/${bench}_base.riscv
# path to the folder that stores all the checkpoints
ckpDir=$benchDir/se_checkpoint_dir

# the loop continues until all executions of the benchmark are discovered
while [ -d "$benchDir" ]
do
    simindex=0
    pids=""
    mkdir $index
    cd $index
    dir=$benchDir/se_checkpoint_dir/cpt.SimPoint$simindex

    # the loop continues until all checkpoints of this execution is discovered
    while [ -d "$dir" ]
    do
        # WARNING: with nohup it starts multiple instances of gem5 simulations in parallel
        nohup $gem5optDir --outdir=$simindex restore_script.py --execution=$benchExe --simpoint_path=$benchDir --checkpoint=$ckpDir/cpt.SimPoint$simindex --index=$simindex > nohup-restore-$bench-$size-$index-ckp$simindex-log.txt &

        # this line collects this process id
        pids="$pids $!"

        simindex=$((simindex+1))
        dir=dir=$benchDir/se_checkpoint_dir/cpt.SimPoint$simindex
    done
    index=$((index+1))

    # This part controls the script from starting too much instances of gem5 simulation.
    # The loop only exits when all checkpoints finished restoring for the current execution
    for pid in $pids; do 
        echo "waiting for pid"
        echo $pid
        wait $pid
        echo "done waiting"
    done
    
    cd ..
    benchDir=/projects/gem5/riscv-spec2006/checkpoints/data/$size/$bench/$index
    benchExe=$benchDir/${bench}_base.riscv
    ckpDir=$benchDir/se_checkpoint_dir
done
```


