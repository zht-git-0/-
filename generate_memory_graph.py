import json
import os
import urllib.request

# 配置路径
INPUT_PATH = r"C:\Users\zht\AppData\Local\npm-cache\_npx\15b07286cbcc3329\node_modules\@modelcontextprotocol\server-memory\dist\memory.jsonl"
OUTPUT_FILE = "memory_graph.html"
LIB_URL = "https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"
LIB_FILE = "vis-network.min.js"

# HTML 模板
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>记忆知识图谱</title>
    <!-- 引用本地下载并去除了 SourceMap 引用的 JS 文件 -->
    <script type="text/javascript" src="./vis-network.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        #header {{ background-color: #2d2d2d; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 10; display: flex; justify-content: space-between; align-items: center; height: 60px; box-sizing: border-box; }}
        h1 {{ margin: 0; font-size: 1.2rem; color: #4fc3f7; }}
        
        #main-container {{ flex-grow: 1; display: flex; overflow: hidden; position: relative; }}
        
        #sidebar {{ width: 250px; background-color: #252526; border-right: 1px solid #3e3e42; display: flex; flex-direction: column; z-index: 5; }}
        #search-container {{ padding: 10px; border-bottom: 1px solid #3e3e42; }}
        #search-input {{ width: 100%; padding: 8px; box-sizing: border-box; border-radius: 4px; border: 1px solid #3e3e42; background-color: #333333; color: #e0e0e0; outline: none; }}
        #search-input:focus {{ border-color: #4fc3f7; }}
        
        #node-list {{ list-style: none; padding: 0; margin: 0; overflow-y: auto; flex-grow: 1; }}
        #node-list li {{ padding: 8px 15px; cursor: pointer; border-bottom: 1px solid #2d2d2d; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }}
        #node-list li:hover {{ background-color: #37373d; }}
        #node-list li.active {{ background-color: #37373d; border-left: 3px solid #4fc3f7; }}
        #node-list .node-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}

        #mynetwork {{ flex-grow: 1; height: 100%; background-color: #1e1e1e; }}
        
        #info-panel {{ position: absolute; top: 20px; right: 20px; width: 300px; background-color: rgba(45, 45, 45, 0.95); border: 1px solid #444; border-radius: 8px; padding: 15px; display: none; box-shadow: 0 4px 15px rgba(0,0,0,0.5); backdrop-filter: blur(5px); transition: all 0.3s ease; max-height: 80vh; overflow-y: auto; }}
        #info-panel h3 {{ margin-top: 0; color: #ffb74d; border-bottom: 1px solid #555; padding-bottom: 8px; }}
        #info-panel p {{ margin-bottom: 0; font-size: 0.9rem; line-height: 1.5; color: #ccc; }}
        #info-panel ul {{ padding-left: 20px; margin-top: 10px; }}
        #info-panel li {{ margin-bottom: 5px; font-size: 0.85rem; }}
        
        .legend {{ display: flex; gap: 15px; font-size: 0.8rem; flex-wrap: wrap; margin-right: 20px; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #1e1e1e; }}
        ::-webkit-scrollbar-thumb {{ background: #444; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #555; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>记忆图谱</h1>
        <div class="legend" id="legend-container">
            <!-- Legend items will be injected here -->
        </div>
    </div>
    
    <div id="main-container">
        <div id="sidebar">
            <div id="search-container">
                <input type="text" id="search-input" placeholder="搜索节点..." autocomplete="off">
            </div>
            <ul id="node-list">
                <!-- Node list items will be injected here -->
            </ul>
        </div>
        
        <div id="mynetwork"></div>
        
        <div id="info-panel">
            <h3 id="panel-title"></h3>
            <div id="panel-content"></div>
        </div>
    </div>

    <script type="text/javascript">
        const nodesData = {nodes_json};
        const nodes = new vis.DataSet(nodesData);
        const edges = new vis.DataSet({edges_json});

        // 自动生成图例颜色
        const groupColors = {{
            "Person": {{ background: '#ff7675', border: '#d63031' }},
            "Character": {{ background: '#ff7675', border: '#d63031' }},
            "Item": {{ background: '#74b9ff', border: '#0984e3' }},
            "Concept": {{ background: '#55efc4', border: '#00b894' }},
            "Plan": {{ background: '#81ecec', border: '#00cec9' }},
            "Monster": {{ background: '#a29bfe', border: '#6c5ce7' }},
            "Location": {{ background: '#ffeaa7', border: '#fdcb6e' }},
            "Group": {{ background: '#fab1a0', border: '#e17055' }},
            "Event": {{ background: '#ff9ff3', border: '#fd79a8' }},
            "Other": {{ background: '#dfe6e9', border: '#b2bec3' }}
        }};

        // 注入图例
        const legendContainer = document.getElementById('legend-container');
        const groups = new Set();
        nodes.forEach(node => groups.add(node.group));
        
        groups.forEach(group => {{
            const color = groupColors[group] ? groupColors[group].background : groupColors["Other"].background;
            const span = document.createElement('span');
            span.className = 'legend-item';
            span.innerHTML = `<span class="dot" style="background:${{color}}"></span>${{group}}`;
            legendContainer.appendChild(span);
        }});

        const container = document.getElementById('mynetwork');
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{
                shape: 'dot',
                size: 20,
                font: {{ size: 14, color: '#e0e0e0', strokeWidth: 2, strokeColor: '#1e1e1e' }},
                borderWidth: 2,
                shadow: true,
                scaling: {{ min: 10, max: 30 }}
            }},
            edges: {{
                width: 1,
                color: {{ color: '#666', highlight: '#4fc3f7' }},
                smooth: {{ type: 'continuous' }},
                font: {{ size: 10, align: 'middle', strokeWidth: 0, color: '#aaa', background: 'none' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }}
            }},
            groups: groupColors, 
            physics: {{
                stabilization: false,
                barnesHut: {{ 
                    gravitationalConstant: -5000, 
                    centralGravity: 0.3, 
                    springLength: 300, 
                    springConstant: 0.03, 
                    damping: 0.09, 
                    avoidOverlap: 0.5 
                }},
                minVelocity: 0.75
            }},
            interaction: {{ hover: true, tooltipDelay: 200, multiselect: true }}
        }};

        const network = new vis.Network(container, data, options);

        // --- 侧边栏列表逻辑 ---
        const nodeList = document.getElementById('node-list');
        const searchInput = document.getElementById('search-input');

        function renderNodeList(filterText = '') {{
            nodeList.innerHTML = '';
            const allNodes = nodes.get({{ order: 'label' }}); // Get all nodes sorted by label
            
            allNodes.forEach(node => {{
                if (filterText && !node.label.toLowerCase().includes(filterText.toLowerCase())) {{
                    return;
                }}
                
                const li = document.createElement('li');
                const color = (groupColors[node.group] || groupColors["Other"]).background;
                
                li.innerHTML = `<span class="node-dot" style="background:${{color}}"></span>${{node.label}}`;
                li.onclick = () => focusOnNode(node.id);
                li.dataset.id = node.id;
                nodeList.appendChild(li);
            }});
        }}

        function focusOnNode(nodeId) {{
            network.focus(nodeId, {{
                scale: 1.2,
                animation: {{ duration: 500, easingFunction: 'easeInOutQuad' }}
            }});
            network.selectNodes([nodeId]);
            showInfo(nodes.get(nodeId));
            
            // Highlight list item
            document.querySelectorAll('#node-list li').forEach(li => li.classList.remove('active'));
            const activeLi = document.querySelector(`#node-list li[data-id="${{nodeId}}"]`);
            if (activeLi) activeLi.classList.add('active');
        }}

        searchInput.addEventListener('input', (e) => {{
            renderNodeList(e.target.value);
        }});

        // Initialize list
        renderNodeList();

        // --- 网络图交互 ---
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                showInfo(node);
                
                // Highlight list item
                document.querySelectorAll('#node-list li').forEach(li => li.classList.remove('active'));
                const activeLi = document.querySelector(`#node-list li[data-id="${{nodeId}}"]`);
                if (activeLi) {{
                    activeLi.classList.add('active');
                    activeLi.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
            }} else {{
                hideInfo();
                document.querySelectorAll('#node-list li').forEach(li => li.classList.remove('active'));
            }}
        }});

        function showInfo(node) {{
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('panel-title');
            const content = document.getElementById('panel-content');

            title.innerText = node.label + " (" + (node.group || "Entity") + ")";
            
            let htmlContent = "<ul>";
            if (node.info && node.info.length > 0) {{
                node.info.forEach(item => {{
                    htmlContent += `<li>${{item}}</li>`;
                }});
            }} else {{
                htmlContent += "<li>暂无详细信息</li>";
            }}
            htmlContent += "</ul>";
            
            content.innerHTML = htmlContent;
            panel.style.display = 'block';
        }}

        function hideInfo() {{
            document.getElementById('info-panel').style.display = 'none';
        }}
    </script>
</body>
</html>
"""

def prepare_lib():
    if not os.path.exists(LIB_FILE):
        print(f"Downloading library from {{LIB_URL}}...")
        try:
            with urllib.request.urlopen(LIB_URL) as response:
                content = response.read().decode('utf-8')
                
                # Strip source mapping line
                # Look for //# sourceMappingURL=...
                lines = content.splitlines()
                clean_lines = [line for line in lines if "sourceMappingURL=" not in line]
                clean_content = "\n".join(clean_lines)
                
                with open(LIB_FILE, "w", encoding="utf-8") as f:
                    f.write(clean_content)
                print(f"Library saved and cleaned to {{LIB_FILE}}")
        except Exception as e:
            print(f"Failed to download library: {{e}}")
            # If download fails, maybe creating an empty file or falling back?
            # For now, let's just warn.

def main():
    prepare_lib()
    
    nodes = []
    edges = []
    
    existing_nodes = set()
    node_map = {} # Map lower case name to real name to handle some inconsistencies if needed

    print(f"Reading from: {{INPUT_PATH}}")
    
    try:
        with open(INPUT_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    
                    if record['type'] == 'entity':
                        name = record.get('name', 'Unknown')
                        entity_type = record.get('entityType', 'Other')
                        observations = record.get('observations', [])
                        
                        if not entity_type:
                            entity_type = "Other"
                        if entity_type == "Character": entity_type = "Person"

                        node = {
                            "id": name,
                            "label": name,
                            "group": entity_type,
                            "title": "点击查看详情",
                            "info": observations
                        }
                        
                        # Overwrite if exists
                        nodes = [n for n in nodes if n['id'] != name]
                        nodes.append(node)
                        existing_nodes.add(name)
                        node_map[name] = name
                        
                    elif record['type'] == 'relation':
                        source = record.get('from')
                        target = record.get('to')
                        relation = record.get('relationType', 'related to')
                        
                        if source and target:
                            edge = {
                                "from": source,
                                "to": target,
                                "label": relation,
                                "arrows": "to"
                            }
                            edges.append(edge)
                            
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {{line[:50]}}...")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File not found at {{INPUT_PATH}}")
        return

    # Filter edges
    # Be more lenient? If source exists, good.
    valid_edges = [e for e in edges if e['from'] in existing_nodes and e['to'] in existing_nodes]

    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(valid_edges, ensure_ascii=False)

    html_content = HTML_TEMPLATE.format(nodes_json=nodes_json, edges_json=edges_json)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Successfully generated {{OUTPUT_FILE}}")
    print(f"Nodes: {{len(nodes)}}, Edges: {{len(valid_edges)}}")

if __name__ == "__main__":
    main()
