from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from pathlib import Path

requires(isa_required=ISA.X86)
cache_hierarchy = NoCache()
memory = SingleChannelDDR3_1600(size="2GB")
processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86,
    num_cores=9,
)
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)
board.set_se_binary_workload(
    binary=obtain_resource("x86-matrix-multiply-omp"),
    # In here, we use the gem5 resource to obtain the binary
    # we can also input the local path to the binary, i.e.
    # binary=Path("path/to/binary")
    arguments=[100, 8]
)

simulator = Simulator(
    board=board
)
simulator.run()