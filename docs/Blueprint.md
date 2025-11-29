# The blueprint

`Viviphi` is a python library that turns static graphs into beautiful animations.
The input is a `mermaid` string, and the output is an SVG animation.

## Steps
The process of creating an animation with `Viviphi` can be broken down into the following steps:
1. `Viviphi` takes a `mermaid` string and (optionally) a description string as input.
2. It generates intermediate frames as `mermaid` strings based on the input graph and description.
3. Each `mermaid` string is converted into an SVG frame using the `mermaid-cli` tool.
4. The SVG frames are combined into a single animated SVG file.


## Details
If a description is provided, `Viviphi` calles an LLM (like `Claude` or `GPT-4`) to generate a series of intermediate `mermaid` graphs that illustrate the steps described in the description.
If no description is provided, `Viviphi` passes the input graph to the LLM and asks it to generate a description of the graph first.
