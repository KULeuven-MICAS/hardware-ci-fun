# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0


import subprocess
import cocotb
from cocotb.triggers import Decimal, Timer
from cocotb_test.simulator import run



async def generate_clock(dut):
    """Generate clock pulses."""

    for _ in range(20):
        dut.clk_i.value = 0
        await Timer(Decimal(1), units="ns")
        dut.clk_i.value = 1
        await Timer(Decimal(1), units="ns")


@cocotb.test()
async def my_test(dut):
    """Use the counter for 5 counts."""

    await cocotb.start(generate_clock(dut))  # run the clock "in the background"
    dut.rst_ni.value = 0
    await Timer(Decimal(1), units="ns")
    dut.rst_ni.value = 1
    dut.clear_i.value = 0
    dut.en_i.value = 1
    dut.d_i.value = 0
    dut.load_i.value = 0
    dut.delta_i.value = 1
    await Timer(Decimal(10), units ="ns")
    # After 5 cycles of being enabled, the count of the 4 bit counter should be 5
    assert dut.q_o.value == 5


def test_the_design():
    bender_output = subprocess.run(["bender", "script", "flist", "--target=verilator"], capture_output=True)
    bender_file_list = bender_output.stdout.decode().rstrip("\n").split("\n")
    verilog_sources = [path for path in bender_file_list if "+incdir+" not in path and "counter" in path]
    includes = [path.lstrip("+incdir+") for path in bender_file_list if "+incdir+" in path]
    run(
        simulator="verilator",
        verilog_sources=verilog_sources,
        includes=includes,
        toplevel=["delta_counter"],
        module="test_delta_counter",
        parameters={"WIDTH":"4", "STICKY_OVERFLOW":"1'b0"}
    )
