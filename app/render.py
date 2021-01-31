from textwrap import dedent


def headline(entry):
    authors = "".join(
        [f'<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">{author.name}</span>'
                          for author in entry.authors])
    tags = "".join(
        [f'<span class="px-2 inline-flex text-xs leading-5 rounded-full bg-blue-100 text-blue-800">{tag.term}</span>'
         for tag in entry.tags]
    )
    return dedent(f"""
        <tr>
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
            <div class="flex-shrink-1">
              <img class="h-4 w-4 rounded-full" src="{entry.icon}" alt="">
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {entry.title}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {authors}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {tags}
          </td>
        </tr>
        """)