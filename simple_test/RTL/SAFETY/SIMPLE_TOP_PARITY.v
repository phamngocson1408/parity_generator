`timescale 1ns / 1ps

module SIMPLE_TOP_IP_PARITY_GEN (
    input ACLK, RESETN_ACLK,
    input  FIERR_WADDR_PARITY,
    input  [32-1:0] WADDR_DATA,
    output [1-1:0] WADDR_PARITY,
    input  WADDR_VALID,
    input  [64-1:0] WDATA_DATA,
    output [1-1:0] WDATA_PARITY,
    input  WDATA_VALID,
    input  [32-1:0] RADDR_DATA,
    output [1-1:0] RADDR_PARITY,
    input  RADDR_VALID,
    input  [64-1:0] RDATA_DATA,
    input  [1-1:0] RDATA_PARITY,
    input  RDATA_VALID
);


reg r_FIERR_WADDR_PARITY;
BOS_SOC_SYNCHSR #(.DW(1)) u_bos_synch_FIERR_WADDR_PARITY (
    .I_CLK (ACLK),
    .I_RESETN (RESETN_ACLK),
    .I_D (FIERR_WADDR_PARITY),
    .O_Q (r_FIERR_WADDR_PARITY)
);

reg r_ENERR_WADDR_PARITY;
BOS_SOC_SYNCHSR #(.DW(1)) u_bos_synch_ENERR_WADDR_PARITY (
    .I_CLK (ACLK),
    .I_RESETN (RESETN_ACLK),
    .I_D (ENERR_WADDR_PARITY),
    .O_Q (r_ENERR_WADDR_PARITY)
);


assign WADDR_PARITY[0] = WADDR_VALID ? (^WADDR_DATA[31:0]) : 1'b0;

assign WDATA_PARITY[0] = WDATA_VALID ? (^WDATA_DATA[63:0]) : 1'b0;

assign RADDR_PARITY[0] = RADDR_VALID ? (^RADDR_DATA[31:0]) : 1'b0;

wire [64-1:0] w_RDATA_DATA_gated = RDATA_VALID ? RDATA_DATA : 64'b0;
wire w_rdata_data_parity_0 = ^w_RDATA_DATA_gated[63:0];


wire w_AnyError_SIMPLE_TOP;
DCLS_COMPARATOR_TEMPLATE #(
    .DATA_WIDTH(1),
    .MAX_INPUT_WIDTH(64),
    .NUM_OR_STAGES(0)
) u_comparator_simple_top (
    .CLK(ACLK),
    .RESETN(RESETN_ACLK),
    .DATA_IN_A({ RDATA_PARITY}),
    .DATA_IN_B({ w_rdata_data_parity_0 }),
    .ENERR_DCLS(r_ENERR_WADDR_PARITY),
    .FIERR_DCLS(r_FIERR_WADDR_PARITY),
    .ERR_DCLS(ERR_WADDR_PARITY),
    .ERR_DCLS_B(ERR_WADDR_PARITY_B)
);

endmodule

