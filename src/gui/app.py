"""Tkinter graphical interface for interactive P2P searches."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any

import networkx as nx

from src.algorithms import TraceEvent
from src.config.loader import ConfigLoader, NetworkConfig
from src.gui.graph_layout import Point, edge_key, scale_positions
from src.network.network import P2PNetwork
from src.simulation.report import format_search_result
from src.simulation.search_simulator import SearchSimulator
from src.validators.network_validator import NetworkValidator

NODE_RADIUS = 20
ANIMATION_DELAY_MS = 850
NODE_NORMAL = "#FFFFFF"
NODE_VISITED = "#D9ECFF"
NODE_FOUND = "#C8F7D4"
NODE_EXPIRED = "#FFE2B8"
EDGE_NORMAL = "#8A94A6"
EDGE_ACTIVE = "#D64545"
EDGE_BACKTRACK = "#6F5BD8"


class P2PSearchApp:
    """Interactive desktop application for running search simulations."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Simulador P2P")
        self._root.geometry("980x680")
        self._root.minsize(820, 560)

        self._config: NetworkConfig | None = None
        self._network: P2PNetwork | None = None
        self._simulator: SearchSimulator | None = None
        self._last_report = ""
        self._last_trace: tuple[TraceEvent, ...] = ()
        self._animation_after_id: str | None = None
        self._animation_index = 0
        self._found_nodes: set[str] = set()
        self._node_positions: dict[str, Point] = {}
        self._node_items: dict[str, int] = {}
        self._node_label_items: dict[str, int] = {}
        self._edge_items: dict[tuple[str, str], int] = {}

        self._config_path = tk.StringVar(value="")
        self._seed = tk.StringVar(value="42")
        self._node_id = tk.StringVar(value="")
        self._resource_id = tk.StringVar(value="")
        self._ttl = tk.StringVar(value="3")
        self._algorithm = tk.StringVar(value="")
        self._status = tk.StringVar(value="Carregue uma topologia YAML para iniciar.")

        self._build_layout()

    def _build_layout(self) -> None:
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(2, weight=1)

        file_frame = ttk.LabelFrame(self._root, text="Topologia")
        file_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Arquivo YAML").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(file_frame, textvariable=self._config_path).grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        ttk.Button(file_frame, text="Procurar", command=self._choose_config).grid(row=0, column=2, padx=8, pady=8)
        ttk.Button(file_frame, text="Carregar rede", command=self._load_config).grid(row=0, column=3, padx=8, pady=8)

        controls = ttk.LabelFrame(self._root, text="Busca")
        controls.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        for column in range(9):
            controls.columnconfigure(column, weight=1)

        ttk.Label(controls, text="No inicial").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        self._node_combo = ttk.Combobox(controls, textvariable=self._node_id, state="disabled")
        self._node_combo.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(controls, text="Recurso").grid(row=0, column=1, sticky="w", padx=8, pady=(8, 2))
        self._resource_combo = ttk.Combobox(controls, textvariable=self._resource_id, state="disabled")
        self._resource_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(controls, text="TTL").grid(row=0, column=2, sticky="w", padx=8, pady=(8, 2))
        ttk.Spinbox(controls, from_=0, to=999, textvariable=self._ttl, width=8).grid(
            row=1,
            column=2,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )

        ttk.Label(controls, text="Algoritmo").grid(row=0, column=3, sticky="w", padx=8, pady=(8, 2))
        self._algorithm_combo = ttk.Combobox(controls, textvariable=self._algorithm, state="disabled")
        self._algorithm_combo.grid(row=1, column=3, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(controls, text="Seed").grid(row=0, column=4, sticky="w", padx=8, pady=(8, 2))
        ttk.Entry(controls, textvariable=self._seed, width=8).grid(row=1, column=4, sticky="ew", padx=8, pady=(0, 8))

        self._run_button = ttk.Button(controls, text="Executar busca", command=self._run_search, state="disabled")
        self._run_button.grid(row=1, column=5, sticky="ew", padx=8, pady=(0, 8))

        self._save_button = ttk.Button(controls, text="Salvar rastro", command=self._save_report, state="disabled")
        self._save_button.grid(row=1, column=6, sticky="ew", padx=8, pady=(0, 8))

        self._animate_button = ttk.Button(controls, text="Animar busca", command=self._replay_animation, state="disabled")
        self._animate_button.grid(row=1, column=7, sticky="ew", padx=8, pady=(0, 8))

        ttk.Button(controls, text="Limpar", command=self._clear_report).grid(
            row=1,
            column=8,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )

        content = ttk.PanedWindow(self._root, orient=tk.HORIZONTAL)
        content.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)

        graph_frame = ttk.LabelFrame(content, text="Rede P2P")
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        content.add(graph_frame, weight=1)

        self._canvas = tk.Canvas(graph_frame, background="#F8FAFC", highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self._canvas.bind("<Configure>", self._redraw_network)

        legend = ttk.Frame(graph_frame)
        legend.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._add_legend_item(legend, 0, NODE_NORMAL, "nao visitado")
        self._add_legend_item(legend, 1, NODE_VISITED, "visitado")
        self._add_legend_item(legend, 2, NODE_FOUND, "encontrado")
        self._add_legend_item(legend, 3, NODE_EXPIRED, "ttl 0")

        report_frame = ttk.LabelFrame(content, text="Resultado e passo a passo")
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(0, weight=1)
        content.add(report_frame, weight=1)

        self._report = scrolledtext.ScrolledText(report_frame, wrap="word", height=20)
        self._report.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self._report.configure(state="disabled")

        status_bar = ttk.Label(self._root, textvariable=self._status, anchor="w")
        status_bar.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))

    def _add_legend_item(self, parent: ttk.Frame, column: int, color: str, text: str) -> None:
        item = ttk.Frame(parent)
        item.grid(row=0, column=column, sticky="w", padx=(0, 16))
        sample = tk.Canvas(item, width=18, height=18, highlightthickness=0)
        sample.grid(row=0, column=0, padx=(0, 4))
        sample.create_oval(2, 2, 16, 16, fill=color, outline="#334155")
        ttk.Label(item, text=text).grid(row=0, column=1)

    def _choose_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar topologia YAML",
            filetypes=[("Arquivos YAML", "*.yaml *.yml"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self._config_path.set(path)

    def _load_config(self) -> None:
        try:
            seed = int(self._seed.get())
            config = ConfigLoader.load(self._config_path.get())
            NetworkValidator().validate(config)
        except (OSError, ValueError) as error:
            messagebox.showerror("Erro ao carregar rede", str(error))
            self._status.set("Falha ao carregar a topologia.")
            return

        network = config.to_network()
        simulator = SearchSimulator(network, seed=seed)
        self._config = config
        self._network = network
        self._simulator = simulator
        self._last_trace = ()
        self._update_available_values(config, simulator)
        self._draw_network()
        self._animate_button.configure(state="disabled")
        self._status.set(f"Rede carregada: {Path(self._config_path.get()).name}")

    def _update_available_values(self, config: NetworkConfig, simulator: SearchSimulator) -> None:
        nodes = sorted(config.resources)
        resources = sorted({resource for node_resources in config.resources.values() for resource in node_resources})

        self._node_combo.configure(values=nodes, state="readonly")
        self._resource_combo.configure(values=resources, state="readonly")
        self._algorithm_combo.configure(values=simulator.algorithms, state="readonly")
        self._run_button.configure(state="normal")

        if nodes:
            self._node_id.set(nodes[0])
        if resources:
            self._resource_id.set(resources[0])
        if simulator.algorithms:
            self._algorithm.set(simulator.algorithms[0])

    def _run_search(self) -> None:
        if self._simulator is None:
            messagebox.showwarning("Rede ausente", "Carregue uma topologia antes de executar a busca.")
            return

        try:
            ttl = int(self._ttl.get())
            result = self._simulator.run(
                node_id=self._node_id.get(),
                resource_id=self._resource_id.get(),
                ttl=ttl,
                algo=self._algorithm.get(),
            )
        except ValueError as error:
            messagebox.showerror("Erro na busca", str(error))
            return

        self._last_report = format_search_result(result)
        self._last_trace = result.trace
        self._set_report(self._last_report)
        self._save_button.configure(state="normal")
        self._animate_button.configure(state="normal")
        self._status.set("Busca executada com sucesso.")
        self._start_animation()

    def _save_report(self) -> None:
        if not self._last_report:
            messagebox.showwarning("Rastro ausente", "Execute uma busca antes de salvar o rastro.")
            return

        path = filedialog.asksaveasfilename(
            title="Salvar rastro",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return

        try:
            Path(path).write_text(self._last_report + "\n", encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Erro ao salvar rastro", str(error))
            return
        self._status.set(f"Rastro salvo em: {path}")

    def _clear_report(self) -> None:
        self._cancel_animation()
        self._last_report = ""
        self._last_trace = ()
        self._set_report("")
        self._save_button.configure(state="disabled")
        self._animate_button.configure(state="disabled")
        self._reset_network_styles()
        self._status.set("Relatorio limpo.")

    def _set_report(self, text: str) -> None:
        self._report.configure(state="normal")
        self._report.delete("1.0", tk.END)
        self._report.insert(tk.END, text)
        self._report.configure(state="disabled")

    def _redraw_network(self, _event: object | None = None) -> None:
        if self._network is not None:
            self._draw_network()

    def _draw_network(self) -> None:
        self._canvas.delete("all")
        self._node_items.clear()
        self._node_label_items.clear()
        self._edge_items.clear()
        self._node_positions.clear()
        self._found_nodes.clear()

        if self._network is None or self._config is None:
            self._canvas.create_text(
                self._canvas.winfo_width() // 2,
                self._canvas.winfo_height() // 2,
                text="Carregue uma topologia YAML",
                fill="#475569",
            )
            return

        width = max(self._canvas.winfo_width(), 320)
        height = max(self._canvas.winfo_height(), 280)
        raw_positions: dict[Any, Any] = nx.spring_layout(self._network.graph, seed=42)
        base_positions = {
            node_id: (float(raw_positions[node_id][0]), float(raw_positions[node_id][1]))
            for node_id in self._network.node_ids
        }
        self._node_positions = scale_positions(base_positions, width=width, height=height)

        for node_a, node_b in sorted((str(a), str(b)) for a, b in self._network.graph.edges):
            x1, y1 = self._node_positions[node_a]
            x2, y2 = self._node_positions[node_b]
            item_id = self._canvas.create_line(x1, y1, x2, y2, fill=EDGE_NORMAL, width=2)
            self._edge_items[edge_key(node_a, node_b)] = item_id

        for node_id in self._network.node_ids:
            x, y = self._node_positions[node_id]
            oval_id = self._canvas.create_oval(
                x - NODE_RADIUS,
                y - NODE_RADIUS,
                x + NODE_RADIUS,
                y + NODE_RADIUS,
                fill=NODE_NORMAL,
                outline="#334155",
                width=2,
            )
            label_id = self._canvas.create_text(x, y, text=node_id, fill="#0F172A", font=("Arial", 10, "bold"))
            resources = ",".join(self._config.resources[node_id])
            self._canvas.create_text(x, y + NODE_RADIUS + 13, text=resources, fill="#475569", font=("Arial", 8))
            self._node_items[node_id] = oval_id
            self._node_label_items[node_id] = label_id

    def _reset_network_styles(self) -> None:
        self._cancel_animation()
        self._found_nodes.clear()
        for item_id in self._edge_items.values():
            self._canvas.itemconfigure(item_id, fill=EDGE_NORMAL, width=2)
        for item_id in self._node_items.values():
            self._canvas.itemconfigure(item_id, fill=NODE_NORMAL, outline="#334155", width=2)

    def _start_animation(self) -> None:
        if not self._last_trace:
            return
        self._cancel_animation()
        self._reset_network_styles()
        self._animation_index = 0
        self._run_button.configure(state="disabled")
        self._animate_button.configure(state="disabled")
        self._advance_animation()

    def _replay_animation(self) -> None:
        if not self._last_trace:
            messagebox.showwarning("Busca ausente", "Execute uma busca antes de animar.")
            return
        self._start_animation()

    def _advance_animation(self) -> None:
        if self._animation_index >= len(self._last_trace):
            self._animation_after_id = None
            self._run_button.configure(state="normal")
            self._animate_button.configure(state="normal")
            self._status.set("Animacao finalizada.")
            return

        event = self._last_trace[self._animation_index]
        self._apply_trace_event(event)
        self._animation_index += 1
        self._animation_after_id = self._root.after(ANIMATION_DELAY_MS, self._advance_animation)

    def _apply_trace_event(self, event: TraceEvent) -> None:
        for item_id in self._edge_items.values():
            self._canvas.itemconfigure(item_id, fill=EDGE_NORMAL, width=2)

        if event.event in {"send", "backtrack"} and event.from_node and event.to_node:
            color = EDGE_BACKTRACK if event.event == "backtrack" else EDGE_ACTIVE
            edge_item = self._edge_items.get(edge_key(event.from_node, event.to_node))
            if edge_item is not None:
                self._canvas.itemconfigure(edge_item, fill=color, width=4)
            self._set_node_color(event.from_node, NODE_VISITED)
            self._set_node_color(event.to_node, NODE_VISITED)
        elif event.event == "visit":
            self._set_node_color(event.node_id, NODE_VISITED)
        elif event.event == "found":
            self._found_nodes.add(event.node_id)
            self._set_node_color(event.node_id, NODE_FOUND)
        elif event.event == "ttl_expired" and event.node_id not in self._found_nodes:
            self._set_node_color(event.node_id, NODE_EXPIRED)

        self._status.set(event.message)

    def _set_node_color(self, node_id: str, color: str) -> None:
        item_id = self._node_items.get(node_id)
        if item_id is None:
            return
        if node_id in self._found_nodes and color != NODE_FOUND:
            return
        self._canvas.itemconfigure(item_id, fill=color)

    def _cancel_animation(self) -> None:
        if self._animation_after_id is None:
            return
        self._root.after_cancel(self._animation_after_id)
        self._animation_after_id = None


def main() -> None:
    """Open the graphical interface."""

    root = tk.Tk()
    P2PSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
