# Copyright (c) 2022 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
from gem5.simulate.exit_event_generators import (
    looppoint_save_checkpoint_generator,
)
from gem5.resources.looppoint import LooppointCreatorCSV

requires(isa_required=ISA.X86)

cache_hierarchy = NoCache()
memory = SingleChannelDDR3_1600(size="2GB")
processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86,
    num_cores=9,
)

looppoint = LooppointCreatorCSV(
    # Pass in the LoopPoint data file
    pinpoints_file=Path(
        obtain_resource(
            "x86-matrix-multiply-omp-100-8-global-pinpoints"
        ).get_local_path()
    )
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_looppoint_workload(
    binary=obtain_resource("x86-matrix-multiply-omp"),
    arguments=[100, 8],
    # Pass LoopPoint module into the board
    looppoint=looppoint,
)

# name the path of where the checkpoints should be saved
dir = Path("looppoint_checkpoints_folder")
dir.mkdir(exist_ok=True)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.SIMPOINT_BEGIN: looppoint_save_checkpoint_generator(
            checkpoint_dir=dir,
            looppoint=looppoint,
            # True if the relative PC count pairs should be updated during the
            # simulation. Default as True.
            update_relatives=True,
            # True if the simulation loop should exit after all the PC count
            # pairs in the LoopPoint data file have been encountered. Default
            # as True.
            exit_when_empty=True,
        )
    },
)

simulator.run()

# Output the JSON file
looppoint.output_json_file()
