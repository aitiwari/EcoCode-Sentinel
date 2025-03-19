// Resource-Intensive Processing
public class DataProcessor {
    // Inefficient memory usage
    public String processData(List<String> inputs) {
        String result = "";
        for (String input : inputs) {
            result += input.toUpperCase(); // String concatenation in loop
        }
        return result;
    }

    // Optimized version
    public String processDataEfficient(List<String> inputs) {
        StringBuilder sb = new StringBuilder();
        inputs.stream()
              .map(String::toUpperCase)
              .forEach(sb::append);
        return sb.toString();
    }
}