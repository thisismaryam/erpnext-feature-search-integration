// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.pages["erpnext-assistant"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ERPNext Assistant"),
		single_column: true,
	});

	wrapper.erpnext_assistant = new erpnext.ERPNextAssistant(wrapper);
	frappe.breadcrumbs.add("Setup");
};

erpnext.ERPNextAssistant = class ERPNextAssistant {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.render();
	}

	render() {
		this.$container = $('<section class="erpnext-assistant"></section>').appendTo(
			$(this.wrapper).find(".layout-main-section")
		);
		this.$messages = $(
			'<div class="erpnext-assistant-messages" role="log" aria-live="polite"></div>'
		).appendTo(this.$container);
		$("<p>")
			.addClass("text-muted")
			.text(
				__(
					"Ask about ERPNext features or request a new User. User requests are saved for review and do not create an account until an authorized reviewer approves them."
				)
			)
			.appendTo(this.$container);
		this.$form = $(
			`<form class="erpnext-assistant-form">
				<label for="erpnext-assistant-question">${__("Ask about ERPNext or request a User")}</label>
				<textarea id="erpnext-assistant-question" maxlength="2000" rows="3" required></textarea>
				<button class="btn btn-primary" type="submit">${__("Ask")}</button>
			</form>`
		).appendTo(this.$container);
		this.$input = this.$form.find("textarea");
		this.$form.on("submit", (event) => this.submit(event));
		this.$input.on("keydown", (event) => {
			if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
				event.preventDefault();
				this.$form.trigger("submit");
			}
		});
		this.add_message(
			"assistant",
			__("Ask me about ERPNext DocTypes, reports, modules, and their fields.")
		);
	}

	add_message(role, content) {
		$("<div>")
			.addClass(`erpnext-assistant-message erpnext-assistant-${role}`)
			.text(content)
			.appendTo(this.$messages);
		this.$messages.scrollTop(this.$messages[0].scrollHeight);
	}

	add_sources(sources) {
		if (!sources?.length) return;

		const $sources = $("<ul>").addClass("erpnext-assistant-sources");
		sources.forEach((source) => {
			const $link = $("<a>")
				.attr("href", "#")
				.text(`${source.name}${source.module ? ` (${source.module})` : ""}`)
				.on("click", (event) => {
					event.preventDefault();
					this.open_source(source);
				});
			$("<li>").append($link).appendTo($sources);
		});
		this.$messages.append($sources);
	}

	add_user_creation_request_link(name) {
		const $link = $("<a>")
			.attr("href", "#")
			.text(__("Review User creation request"))
			.on("click", (event) => {
				event.preventDefault();
				frappe.set_route("Form", "User Creation Request", name);
			});
		$("<p>").addClass("erpnext-assistant-request-link").append($link).appendTo(this.$messages);
	}

	open_source(source) {
		if (source.feature_type === "Report") {
			frappe.set_route("query-report", source.name);
			return;
		}

		frappe.set_route("List", source.name);
	}

	async submit(event) {
		event.preventDefault();
		const question = this.$input.val().trim();
		if (!question) return;

		this.add_message("user", question);
		this.$input.val("").prop("disabled", true);
		this.$form.find("button").prop("disabled", true);

		try {
			const response = await frappe.call({
				method: "erpnext.utilities.page.erpnext_assistant.erpnext_assistant.handle_assistant_question",
				args: { question },
			});
			const result = response.message;
			if (result.action === "user_creation_request") {
				this.add_message("assistant", result.answer);
				this.add_user_creation_request_link(result.request_name);
				return;
			}

			const exactMatch = result.sources?.find(
				(source) => source.similarity_score === 100.0
			);
			if (exactMatch) {
				this.open_source(exactMatch);
				return;
			}

			this.add_message("assistant", result.answer);
			this.add_sources(result.sources);
		} catch (error) {
			this.add_message(
				"assistant",
				error?.message || __("The assistant could not complete the request.")
			);
		} finally {
			this.$input.prop("disabled", false).trigger("focus");
			this.$form.find("button").prop("disabled", false);
		}
	}
};
