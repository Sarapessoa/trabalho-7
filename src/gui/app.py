"""Tkinter graphical interface for interactive P2P searches."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.config.loader import ConfigLoader, NetworkConfig
from src.simulation.report import format_search_result
from src.simulation.search_simulator import SearchSimulator
from src.validators.network_validator import NetworkValidator


class P2PSearchApp:
    """Interactive desktop application for running search simulations."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Simulador P2P")
        self._root.geometry("980x680")
        self._root.minsize(820, 560)

        self._config: NetworkConfig | None = None
        self._simulator: SearchSimulator | None = None
        self._last_report = ""

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
        for column in range(8):
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

        ttk.Button(controls, text="Limpar", command=self._clear_report).grid(
            row=1,
            column=7,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )

        report_frame = ttk.LabelFrame(self._root, text="Resultado e passo a passo")
        report_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(0, weight=1)

        self._report = scrolledtext.ScrolledText(report_frame, wrap="word", height=20)
        self._report.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self._report.configure(state="disabled")

        status_bar = ttk.Label(self._root, textvariable=self._status, anchor="w")
        status_bar.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))

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

        simulator = SearchSimulator(config.to_network(), seed=seed)
        self._config = config
        self._simulator = simulator
        self._update_available_values(config, simulator)
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
        self._set_report(self._last_report)
        self._save_button.configure(state="normal")
        self._status.set("Busca executada com sucesso.")

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
        self._last_report = ""
        self._set_report("")
        self._save_button.configure(state="disabled")
        self._status.set("Relatorio limpo.")

    def _set_report(self, text: str) -> None:
        self._report.configure(state="normal")
        self._report.delete("1.0", tk.END)
        self._report.insert(tk.END, text)
        self._report.configure(state="disabled")


def main() -> None:
    """Open the graphical interface."""

    root = tk.Tk()
    P2PSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
