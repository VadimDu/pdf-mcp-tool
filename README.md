# FastMCP-based PDF Tool for LLM/agents frontends such as LM-Studio

A Python tool that lets LLMs extract and read pages from PDF files using the **MCP protocol**, designed for use with frontends such as [LM Studio](https://lmstudio.ai).

## ✅ Features

- Extract text from specific pages range in a PDF
- Optionally save extracted pages as a new PDF file
- Input validation with Pydantic scheme
- Works seamlessly with LM Studio via MCP protocol

## 🚀 Installation

Install directly from GitHub:

```
pip install git+https://github.com/VadimDu/pdf-mcp-tool.git
```

Or install in development mode:

```
git clone https://github.com/VadimDu/pdf-mcp-tool.git
cd pdf-tool
pip install -e .
```

## 🛠 Testing

To test the this mcp-tool before real usage by LLM/agent:
```
python -m pdf_tool.pdf_tool_mcp_server
```
or
```
fastmcp run pdf_tool/pdf_tool_mcp_server.py
```
If everything is working fine, you should see a message like this:
`[date time] INFO     Starting MCP server 'PDF-tool' with transport 'stdio'`

## 🎉 Usage in LM Studio

Add the following to your `mcp.json` file:
```
{
	"pdf-tool": {
      "command": "python",
      "args": [
        "-m",
        "pdf_tool.pdf_tool_mcp_server"
      ]
    }
}
```
