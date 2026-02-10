`timescale 1ns / 1ps

// MD5@INFO : 305f3681692ea4f39d05961cd6714eeb
// Version@Script : 3.0.0
module SIMPLE_TOP_IP_PARITY_GEN (
    input ACLK, RESETN_ACLK,
    input  ENERR_WADDR_PARITY,
    output ERR_WADDR_PARITY,
    output ERR_WADDR_PARITY_B,
    input  FIERR_WADDR_PARITY,
    input  [32-1:0] WADDR_DATA,
    input  [0:0] WADDR_PARITY,
    input  WADDR_VALID,
    input  [64-1:0] WDATA_DATA,
    input  [0:0] WDATA_PARITY,
    input  WDATA_VALID,
    input  [32-1:0] RADDR_DATA,
    input  [0:0] RADDR_PARITY,
    input  RADDR_VALID,
    input  [64-1:0] RDATA_DATA,
    output [0:0] RDATA_PARITY,
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


wire [32-1:0] w_WADDR_DATA_gated = WADDR_VALID ? WADDR_DATA : 32'b0;
wire w_waddr_data_parity_0 = ^w_WADDR_DATA_gated[31:0];

wire [64-1:0] w_WDATA_DATA_gated = WDATA_VALID ? WDATA_DATA : 64'b0;
wire w_wdata_data_parity_0 = ^w_WDATA_DATA_gated[63:0];

wire [32-1:0] w_RADDR_DATA_gated = RADDR_VALID ? RADDR_DATA : 32'b0;
wire w_raddr_data_parity_0 = ^w_RADDR_DATA_gated[31:0];

assign RDATA_PARITY[0] = RDATA_VALID ? (^RDATA_DATA[63:0]) : 1'b0;


wire w_AnyError_SIMPLE_TOP;
// Gate RECEIVE parity ports with corresponding signal_valid signals
wire [1-1:0] w_WADDR_PARITY_gated = WADDR_VALID ? WADDR_PARITY : 1'b0;
wire [1-1:0] w_WDATA_PARITY_gated = WDATA_VALID ? WDATA_PARITY : 1'b0;
wire [1-1:0] w_RADDR_PARITY_gated = RADDR_VALID ? RADDR_PARITY : 1'b0;

DCLS_COMPARATOR_TEMPLATE #(
    .DATA_WIDTH(3),
    .MAX_INPUT_WIDTH(64),
    .NUM_OR_STAGES(0)
) u_comparator_simple_top (
    .CLK(ACLK),
    .RESETN(RESETN_ACLK),
    .DATA_IN_A({ w_WADDR_PARITY_gated, w_WDATA_PARITY_gated, w_RADDR_PARITY_gated}),
    .DATA_IN_B({ w_waddr_data_parity_0, w_wdata_data_parity_0, w_raddr_data_parity_0 }),
    .ENERR_DCLS(r_ENERR_WADDR_PARITY),
    .FIERR_DCLS(r_FIERR_WADDR_PARITY),
    .ERR_DCLS(ERR_WADDR_PARITY),
    .ERR_DCLS_B(ERR_WADDR_PARITY_B)
);

endmodule

