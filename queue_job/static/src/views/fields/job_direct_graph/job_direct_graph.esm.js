/* @odoo-module */
/* global vis */

import {loadCSS, loadJS} from "@web/core/assets";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

const {Component, onWillStart, useEffect, useRef} = owl;

const {document} = globalThis;

class JobDirectGraph extends Component {
    static props = {...standardFieldProps};
    static template = "queue.JobDirectGraph";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.rootRef = useRef("root_vis");
        this.network = null;
        this.forceRender = false;
        onWillStart(async () => {
            await loadJS("/queue_job/static/lib/vis/vis-network.min.js");
            loadCSS("/queue_job/static/lib/vis/vis-network.min.css");
        });
        useEffect(
            () => {
                this.renderNetwork();
                this._fitNetwork();
                return () => {
                    if (this.network) {
                        this.$el.innerHTML = "";
                    }
                    return this.rootRef.el;
                };
            },
            () => []
        );
    }

    get $el() {
        return this.rootRef.el;
    }

    get resId() {
        return this.props.record.resId;
    }

    get context() {
        return this.props.record.context;
    }

    get model() {
        return this.props.record.resModel;
    }

    htmlTitle(html) {
        const container = document.createElement("div");
        container.innerHTML = html;
        return container;
    }

    renderNetwork() {
        if (this.network) {
            this.$el.innerHTML = "";
        }
        const values = this.props.record.data[this.props.name];
        let nodes = values?.nodes || [];
        if (!nodes.length) {
            return;
        }
        nodes = nodes.map((node) => {
            node.title = this.htmlTitle(node.title || "");
            return node;
        });

        const edges = [];

        (values?.edges || []).forEach((edge) => {
            const edgeFrom = edge[0];
            const edgeTo = edge[1];
            edges.push({
                from: edgeFrom,
                to: edgeTo,
                arrows: "to",
            });
        });

        if (nodes.length * edges.length > 5000 && !this.forceRender) {
            const warningDiv = document.createElement("div");

            warningDiv.className = "alert alert-warning h-100 d-flex";
            warningDiv.className +=
                " flex-column justify-content-center align-items-center";

            warningDiv.innerText =
                `This graph is big (${nodes.length} nodes, ` +
                `${edges.length} edges), it may take a while to display.`;

            const self = this;
            const button = document.createElement("button");
            button.innerText = "Display anyway";
            button.className = "btn btn-secondary";
            button.onclick = function () {
                self.forceRender = true;
                warningDiv.parentNode.removeChild(warningDiv);
                self.renderNetwork();
            };
            warningDiv.appendChild(button);
            this.$el.append(warningDiv);
            return;
        }

        const data = {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges),
        };
        const options = {
            // Fix the seed to have always the same result for the same graph
            layout: {randomSeed: 1},
        };
        // Arbitrary threshold, generation becomes very slow at some
        // point, and disabling the stabilization helps to have a fast result.
        // Actually, it stabilizes, but is displayed while stabilizing, rather
        // than showing a blank canvas.
        if (nodes.length > 100) {
            options.physics = {stabilization: false};
        }
        const network = new vis.Network(this.$el, data, options);
        network.selectNodes([this.resId]);
        var self = this;
        network.on("dragging", function () {
            // By default, dragging changes the selected node
            // to the dragged one, we want to keep the current
            // job selected
            network.selectNodes([self.resId]);
        });
        network.on("click", function (params) {
            if (params.nodes.length > 0) {
                var resId = params.nodes[0];
                if (resId !== self.resId) {
                    self.openDependencyJob(resId);
                }
            } else {
                // Clicked outside of the nodes, we want to
                // keep the current job selected
                network.selectNodes([self.resId]);
            }
        });
        this.network = network;
    }

    async openDependencyJob(resId) {
        const action = await this.orm.call(
            this.model,
            "get_formview_action",
            [[resId]],
            {
                context: this.context,
            }
        );
        await this.action.doAction(action);
    }

    _fitNetwork() {
        if (this.network) {
            this.network.fit(this.network.body.nodeIndices);
        }
    }
}

export const jobDirectGraph = {
    component: JobDirectGraph,
};

registry.category("fields").add("job_directed_graph", jobDirectGraph);
