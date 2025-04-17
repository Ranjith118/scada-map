// Data arrays for storing the devices and links
let nodes = [];
let links = [];

// Default images for device types
const deviceImages = {
    router: "—Pngtree—router vector icon in flat_6358749.png",
    switch: "favpng_network-switch-router-ethernet-hub-clip-art.png",
    computer: "05a7c3bd-cf7f-405b-82e3-d4ea09bfc393.jpg"
};

// D3 SVG Setup
const svg = d3.select("svg");
const width = +svg.attr("width") || 800;
const height = +svg.attr("height") || 600;

// Force simulation for layout
const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Function to render the network
function updateTopology() {
    // Remove old elements
    svg.selectAll("*").remove();

    // Set node positions based on topology
    setNodePositions();

    // Add links
    const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .enter()
        .append("line")
        .attr("stroke", "#999")
        .attr("stroke-width", 2);

    // Add nodes (devices)
    const node = svg.append("g")
        .selectAll("image")
        .data(nodes)
        .enter()
        .append("image")
        .attr("xlink:href", d => d.image)
        .attr("width", 40)
        .attr("height", 40)
        .attr("x", d => d.x || width / 2)
        .attr("y", d => d.y || height / 2)
        .call(drag(simulation));

    // Add labels (device names)
    svg.append("g")
        .selectAll("text")
        .data(nodes)
        .enter()
        .append("text")
        .attr("x", d => d.x || width / 2)
        .attr("y", d => d.y || height / 2 + 25) // Positioning the text slightly below the device
        .text(d => d.id) // The device name will be displayed here
        .attr("font-size", "12px")
        .attr("text-anchor", "middle");

    // Update simulation
    simulation.nodes(nodes).on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("x", d => d.x - 20)
            .attr("y", d => d.y - 20);

        svg.selectAll("text")
            .attr("x", d => d.x || width / 2)
            .attr("y", d => d.y || height / 2 + 25);
    });

    simulation.force("link").links(links);
    simulation.alpha(1).restart();
}

// Set positions of nodes based on topology type
function setNodePositions() {
    const topologyType = document.getElementById("topology-type").value;
    const radius = 200; // Radius for circular arrangement

    // Get devices based on type
    const routers = nodes.filter(n => n.id.startsWith("router"));
    const switches = nodes.filter(n => n.id.startsWith("switch"));
    const computers = nodes.filter(n => n.id.startsWith("computer"));

    if (topologyType === "star") {
        if (routers.length > 0) {
            routers[0].x = width / 2;
            routers[0].y = height / 2;
        }

        const angleIncrement = (2 * Math.PI) / (routers.length + switches.length + computers.length);
        let angle = 0;

        routers.slice(1).forEach((router) => {
            router.x = width / 2 + radius * Math.cos(angle);
            router.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });

        switches.forEach((sw) => {
            sw.x = width / 2 + radius * Math.cos(angle);
            sw.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });

        computers.forEach((comp) => {
            comp.x = width / 2 + radius * Math.cos(angle);
            comp.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });
    } else if (topologyType === "bus") {
        const startX = width / 4;
        const spacing = 100;

        routers.forEach((router, i) => {
            router.x = startX + i * spacing;
            router.y = height / 2;
        });

        switches.forEach((sw, i) => {
            sw.x = startX + (routers.length + i) * spacing;
            sw.y = height / 2;
        });

        computers.forEach((comp, i) => {
            comp.x = startX + (routers.length + switches.length + i) * spacing;
            comp.y = height / 2;
        });
    } else if (topologyType === "ring") {
        const totalDevices = routers.length + switches.length + computers.length;
        const angleIncrement = (2 * Math.PI) / totalDevices;
        let angle = 0;

        routers.forEach((router) => {
            router.x = width / 2 + radius * Math.cos(angle);
            router.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });

        switches.forEach((sw) => {
            sw.x = width / 2 + radius * Math.cos(angle);
            sw.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });

        computers.forEach((comp) => {
            comp.x = width / 2 + radius * Math.cos(angle);
            comp.y = height / 2 + radius * Math.sin(angle);
            angle += angleIncrement;
        });
    }
}

// Dragging functionality
function drag(simulation) {
    return d3.drag()
        .on("start", event => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        })
        .on("drag", event => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        })
        .on("end", event => {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        });
}

// Add a device
document.getElementById("add-device").addEventListener("click", () => {
    const deviceType = document.getElementById("device-type").value;
    const imagePath = deviceImages[deviceType];

    const newNode = {
        id: `${deviceType}_${nodes.filter(n => n.id.startsWith(deviceType)).length + 1}`,
        image: imagePath
    };

    nodes.push(newNode);
    updateTopology();
});

// Generate and set topology
document.getElementById("generate-topology").addEventListener("click", () => {
    links = [];

    const routers = nodes.filter(n => n.id.startsWith("router"));
    const switches = nodes.filter(n => n.id.startsWith("switch"));
    const computers = nodes.filter(n => n.id.startsWith("computer"));

    // Logic to connect devices
    routers.forEach((router, i) => {
        // Connect each router to all previous routers
        for (let j = 0; j < i; j++) {
            links.push({ source: router.id, target: routers[j].id });
        }
    });

    switches.forEach((sw, i) => {
        // Connect each switch to a router
        links.push({ source: sw.id, target: routers[i % routers.length].id });
    });

    computers.forEach((comp, i) => {
        // Connect each computer to a switch
        links.push({ source: comp.id, target: switches[i % switches.length].id });
    });

    updateTopology();
});
