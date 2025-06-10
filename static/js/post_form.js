function postFormHandler() {
    return {
        category: "",

        handleCategoryChange(event) {
            const categoryField = event.target.name === "category" ? event.target : document.querySelector('[name="category"]');
            if (categoryField) {
                this.category = categoryField.value;
            }
        },

        init() {
            const categoryField = document.querySelector('[name="category"]');
            if (categoryField) {
                this.category = categoryField.value;
            }
        }
    }
}
